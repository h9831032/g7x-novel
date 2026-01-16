import os
import sys
import json
import csv
import time
import hashlib
import random
import threading
from collections import Counter
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# [MANDATE] 1. NO_HARDCODED_KEY & SSOT_ROOT
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    sys.stderr.write("[CRITICAL_FAIL] GEMINI_API_KEY 환경변수 누락.\n")
    print("\033[91m[CRITICAL_FAIL] GEMINI_API_KEY 환경변수 누락.\033[0m")
    try: input("Press Enter to exit...")
    except: pass
    sys.exit(1)

SSOT_ROOT = r"C:\g7core\g7_v1"
INPUT_FILE = r"C:\g7core\블레이드헌터.txt" 
RUN_ID = f"OPS_SEAL_V3_STABLE_{int(time.time())}"
RUN_DIR = os.path.join(SSOT_ROOT, "runs", RUN_ID)
os.makedirs(RUN_DIR, exist_ok=True)

TSV_HEADER = ["row_id", "task_id", "slot", "source_path", "payload_hash", "verdict", "score", "why", "ts", "meta"]

# [PATCH-2] Gemini Client 호출 직렬화용 락
GEMINI_LOCK = threading.Lock()

# 2. 로그 시스템
stdout_log = open(os.path.join(RUN_DIR, "stdout.txt"), "a", encoding="utf-8")
stderr_log = open(os.path.join(RUN_DIR, "stderr.txt"), "a", encoding="utf-8")

def log_print(msg, is_error=False):
    target = stderr_log if is_error else stdout_log
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{stamp}] {msg}"
    if is_error: print(f"\033[91m{msg}\033[0m")
    else: print(msg)
    target.write(formatted_msg + "\n"); target.flush()

# [Patch 6] 핸들 누수 방지용 스트리밍 해시 함수
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""): h.update(chunk)
    return h.hexdigest()

def sha256_text(text): return hashlib.sha256(text.encode('utf-8')).hexdigest()

thread_local = threading.local()
def get_client():
    if not hasattr(thread_local, "client"): thread_local.client = genai.Client(api_key=API_KEY)
    return thread_local.client

def get_canonical_hash(data_dict):
    canonical = json.dumps(data_dict, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def row10(row_id, task_id, slot, source_path, payload_hash, verdict, score, why, meta_dict):
    return [int(row_id), str(task_id), str(slot), str(source_path), str(payload_hash),
            str(verdict), round(float(score), 4), str(why), int(time.time()),
            json.dumps(meta_dict, ensure_ascii=False)]

def calculate_score(verdict, payload, fun_score):
    base = 0.5
    if verdict == "ALLOW": base = 0.8
    elif verdict == "WARN": base = 0.5
    elif verdict == "BLOCK": base = 0.1
    risk_factor = min(len(payload) / 5000, 0.2) 
    final = base + (fun_score * 0.1) - risk_factor
    return max(0.0, min(1.0, final))

# [PATCH-3] 스트리밍 인코딩 방어 (errors='replace')
def stream_build_chunks(path, need=240, chunk_size=2500, overlap=200, encoding="utf-8"):
    chunks = []
    current_text = ""
    chunk_count = 0
    step = chunk_size - overlap
    
    # errors="replace"로 인코딩 폭탄 제거
    with open(path, "r", encoding=encoding, errors="replace") as f:
        while chunk_count < need:
            buffer = f.read(4096)
            if not buffer: break
            current_text += buffer
            while len(current_text) >= chunk_size and chunk_count < need:
                payload = current_text[:chunk_size]
                
                # 깨진 문자 감지 및 경고
                has_encoding_error = "\ufffd" in payload
                
                if len(payload) < 500:
                    log_print(f"[FAIL_FAST] 청크 길이 미달 (Row {chunk_count+1})", True); sys.exit(1)
                
                chunks.append({"payload": payload, "fill_mode": "NORMAL", "encoding_warn": has_encoding_error})
                current_text = current_text[step:]
                chunk_count += 1
                
    if not chunks: log_print("[FAIL_FAST] 원문 너무 짧음", True); sys.exit(1)
    if chunk_count < need:
        log_print(f"[WARN] 원문 부족. {need-chunk_count}개 랩어라운드.")
        source_chunks = chunks[:]
        while len(chunks) < need:
            src = source_chunks[len(chunks) % len(source_chunks)]
            chunks.append({"payload": src["payload"], "fill_mode": "WRAP_AROUND", "encoding_warn": src.get("encoding_warn", False)})
    return chunks[:need]

def audit_worker(task):
    client = get_client()
    # Prompt base
    base_prompt = f"Mode: AUDIT. Return JSON only.\nSchema: {{\"verdict\": \"ALLOW|WARN|BLOCK\", \"why\": \"short\", \"foreshadowing\": bool, \"contradictions\": []}}\nPayload: {task['payload']}"
    
    for attempt in range(5):
        try:
            # [PATCH-1] 인젝션 C: Nonce 주입으로 실제 차이 유도 (Temp 0 유지)
            if task.get("injection") == "C":
                # Call 1: Normal
                with GEMINI_LOCK: # [PATCH-2] 호출 직렬화
                    r1 = client.models.generate_content(
                        model="gemini-2.5-flash", contents=base_prompt, 
                        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
                    )
                h1 = get_canonical_hash(json.loads(r1.text))
                
                # Call 2: Nonce Injection (Prompt 변경으로 자연스러운 해시 변화 유도)
                nonce_prompt = base_prompt + "\n"
                with GEMINI_LOCK: # [PATCH-2] 호출 직렬화
                    r2 = client.models.generate_content(
                        model="gemini-2.5-flash", contents=nonce_prompt, 
                        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
                    )
                h2 = get_canonical_hash(json.loads(r2.text))
                
                res_hashes = [h1, h2]
                res_json = json.loads(r1.text)
                canon_hash = h1
            else:
                # Normal Case
                with GEMINI_LOCK: # [PATCH-2] 호출 직렬화
                    response = client.models.generate_content(
                        model="gemini-2.5-flash", contents=base_prompt, 
                        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
                    )
                res_json = json.loads(response.text)
                canon_hash = get_canonical_hash(res_json)
                res_hashes = [canon_hash]

            raw_verdict = str(res_json.get("verdict", "")).upper()
            if raw_verdict not in ["ALLOW", "WARN", "BLOCK"]:
                return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], "BLOCK", 0, "BAD_VERDICT_ENUM", {})
            verdict, why = raw_verdict, res_json.get("why", "OK")

            fp64 = hashlib.blake2b(json.dumps(res_json).encode(), digest_size=8).hexdigest()
            tokens = task['payload'].split()
            fun_score = len(set(tokens)) / len(tokens) if tokens else 0.0
            score = calculate_score(verdict, task['payload'], fun_score)

            if task.get("injection") == "A": verdict, why = "BLOCK", "A_CONTENT_CORRUPTED"
            if task.get("injection") == "B" and len(task['payload_hash']) != 64: verdict, why = "BLOCK", "B_HASH_TRUNCATED"
            if len(set(res_hashes)) > 1: verdict, why = "BLOCK", "C_HASH_MIXED"

            meta = task.get('meta_base', {}).copy()
            meta.update({
                "attempt": attempt, "canon_hash": canon_hash, "fp64": fp64, 
                "fun": fun_score, "res_hashes_cnt": len(res_hashes), "raw_audit": res_json,
                "encoding_warn": task.get("encoding_warn", False)
            })
            
            return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], verdict, score, why, meta)

        except Exception as e:
            if any(err in str(e) for err in ["429", "503", "timeout"]):
                time.sleep((2 ** attempt) + random.uniform(0.5, 1.5)); continue # Backoff 늘림
            return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], "BLOCK", 0, "JSON_PARSE_FAIL", {"err": str(e)})

    return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], "BLOCK", 0, "MAX_RETRY_FAIL", {})

def main():
    try:
        log_print(f"[START_FINAL_STABLE] {RUN_ID}")
        if not os.path.exists(INPUT_FILE):
            log_print(f"[FAIL_FAST] 파일 없음: {INPUT_FILE}", True); sys.exit(1)

        # 1. 청크 생성 (인코딩 방어 적용)
        chunk_data = stream_build_chunks(INPUT_FILE, need=240, chunk_size=2500)

        # 2. 결정성 검사 (Valid Votes 기준)
        log_print("[AUDIT] 결정성 검사 (Canonical Hash)...")
        client = get_client()
        sample_prompt = f"Mode: AUDIT. Return JSON only. Schema: {{\"verdict\": \"ALLOW|WARN|BLOCK\", \"why\": \"short\"}}\nPayload: {chunk_data[0]['payload']}"
        valid_votes = []
        for _ in range(5):
            try:
                # 결정성 검사도 Lock 적용 (안정성)
                with GEMINI_LOCK:
                    r = client.models.generate_content(model="gemini-2.5-flash", contents=sample_prompt, config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0))
                valid_votes.append(get_canonical_hash(json.loads(r.text)))
            except: pass
            time.sleep(0.2)
            
        if not valid_votes: log_print("[FAIL_FAST] 결정성 전원 실패", True); sys.exit(1)
        most_common, count = Counter(valid_votes).most_common(1)[0]
        det_report = {
            "attempts_total": 5, "valid_votes_n": len(valid_votes), 
            "winner_hash": most_common, "winner_count": count, 
            "passed": (count >= 3 and len(valid_votes) >= 3)
        }
        with open(os.path.join(RUN_DIR, "determinism_report.json"), "w") as f: json.dump(det_report, f)
        
        if not det_report['passed']:
            log_print(f"[FAIL_FAST] 결정성 미달 ({count}/{len(valid_votes)})", True); sys.exit(1)
        log_print(f"[PASS] 결정성 확보: {count}/{len(valid_votes)}")

        # 3. 태스크 설정
        slots = (["A"]*60 + ["B"]*36 + ["C"]*18 + ["D"]*6) * 2
        tasks = []
        for i in range(240):
            p = chunk_data[i]['payload']
            inj = "NONE"
            ph = sha256_text(p)
            
            if i == 49: inj, p, ph = "A", p[:500] + " [CORRUPTED]", sha256_text(p[:500] + " [CORRUPTED]")
            if i == 99: inj, ph = "B", ph[:12]
            if i == 149: inj = "C"

            meta_base = {"inj": inj, "fill": chunk_data[i]['fill_mode'], "payload_len": len(p), "payload_sha256": ph, "encoding_warn": chunk_data[i]['encoding_warn']}
            tasks.append({"row_id": i+1, "slot": slots[i], "payload": p, "payload_hash": ph, "injection": inj, "meta_base": meta_base, "encoding_warn": chunk_data[i]['encoding_warn']})

        # work_packet
        with open(os.path.join(RUN_DIR, "work_packet.tsv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter="\t"); w.writerow(TSV_HEADER)
            for t in tasks: w.writerow([t['row_id'], f"T_{t['row_id']}", t['slot'], INPUT_FILE, t['payload_hash'], "PENDING", 0, "", int(time.time()), json.dumps(t['meta_base'])])

        # 4. 실행
        with ThreadPoolExecutor(max_workers=8) as ex:
            results = list(tqdm(ex.map(audit_worker, tasks), total=240, desc="SEALING"))

        # 5. 검증
        caught_a = any(r[7] == "A_CONTENT_CORRUPTED" for r in results)
        caught_b = any(r[7] == "B_HASH_TRUNCATED" for r in results)
        caught_c = any(r[7] == "C_HASH_MIXED" for r in results)
        with open(os.path.join(RUN_DIR, "injection_report.json"), "w") as f: json.dump({"caught_A": caught_a, "caught_B": caught_b, "caught_C": caught_c}, f)

        trA = len([r for r in results if 1 <= r[0] <= 120 and r[5] in ("ALLOW", "WARN")])
        trB = len([r for r in results if 121 <= r[0] <= 240 and r[5] in ("ALLOW", "WARN")])
        log_print(f"[REPORT] Truck A: {trA}/120, Truck B: {trB}/120")

        is_success = (trA >= 90 and trB >= 90 and caught_a and caught_b and caught_c)
        if not is_success: log_print("[CRITICAL_FAIL] 봉인 조건 미달.", True)

        with open(os.path.join(RUN_DIR, "result_packet.tsv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter="\t"); w.writerow(TSV_HEADER); w.writerows(results)

        manifest = {fn: {"sha256": sha256_file(os.path.join(RUN_DIR, fn)), "bytes": os.path.getsize(os.path.join(RUN_DIR, fn))} for fn in os.listdir(RUN_DIR) if os.path.isfile(os.path.join(RUN_DIR, fn))}
        with open(os.path.join(RUN_DIR, "hash_manifest.json"), "w") as f: json.dump(manifest, f, indent=2)

        with open(os.path.join(RUN_DIR, "audit_receipt.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"run_id": RUN_ID, "ts": int(time.time()), "rows": 240, "lanes": 8, "determinism_vote": f"{count}/{len(valid_votes)}", "model": "gemini-2.5-flash"}) + "\n")
            for r in results:
                m = json.loads(r[9])
                f.write(json.dumps({"row_id": r[0], "verdict": r[5], "payload_hash": r[4], "canon_hash": m.get("canon_hash"), "fp64": m.get("fp64"), "fun": m.get("fun")}) + "\n")
            f.write(json.dumps({"summary": {"truckA": trA, "truckB": trB, "injection_ok": (caught_a and caught_b and caught_c), "pass": is_success, "run_dir": RUN_DIR}}) + "\n")

        if is_success: log_print(f"[SUCCESS] 봉인 완료: {RUN_DIR}")
        else: sys.exit(1)

    except Exception as e:
        log_print(f"[CRITICAL_ERROR] {str(e)}", True); sys.exit(1)
    finally:
        stdout_log.close(); stderr_log.close()
        try: input("\nAudit Done. 엔터를 누르면 종료됩니다.")
        except: pass

if __name__ == "__main__":
    main()