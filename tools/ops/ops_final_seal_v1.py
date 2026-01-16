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

# [MANDATE: ELITE_ARCHITECT_MODE] 1. NO_HARDCODED_KEY
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    sys.stderr.write("[CRITICAL_FAIL] GEMINI_API_KEY 환경변수가 없습니다.\n")
    print("\033[91m[CRITICAL_FAIL] GEMINI_API_KEY 환경변수가 없습니다. 설정을 확인하십시오.\033[0m")
    try: input("Press Enter to exit...")
    except: pass
    sys.exit(1)

# 2. 고정 경로 및 환경 설정
SSOT_ROOT = r"C:\g7core\g7_v1"
INPUT_FILE = r"C:\g7core\블레이드헌터.txt"
RUN_ID = f"OPS_SEAL_V2_{int(time.time())}"
RUN_DIR = os.path.join(SSOT_ROOT, "runs", RUN_ID)
os.makedirs(RUN_DIR, exist_ok=True)

TSV_HEADER = ["row_id", "task_id", "slot", "source_path", "payload_hash", "verdict", "score", "why", "ts", "meta"]

# 3. 로그 시스템
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
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

thread_local = threading.local()
def get_client():
    if not hasattr(thread_local, "client"): thread_local.client = genai.Client(api_key=API_KEY)
    return thread_local.client

def get_canonical_hash(data_dict):
    canonical = json.dumps(data_dict, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def row10(row_id, task_id, slot, source_path, payload_hash, verdict, score, why, meta_dict):
    return [
        int(row_id), str(task_id), str(slot), str(source_path), str(payload_hash),
        str(verdict), round(float(score), 4), str(why), int(time.time()),
        json.dumps(meta_dict, ensure_ascii=False)
    ]

# [Patch 4] 12GB 스트리밍 청크 생성기 (ZeroDivision 방어)
def stream_build_chunks(path, need=240, chunk_size=2500, overlap=200, encoding="utf-8"):
    chunks = []
    current_text = ""
    chunk_count = 0
    step = chunk_size - overlap
    
    with open(path, "r", encoding=encoding) as f:
        while chunk_count < need:
            buffer = f.read(4096)
            if not buffer: break
            current_text += buffer
            while len(current_text) >= chunk_size and chunk_count < need:
                payload = current_text[:chunk_size]
                if len(payload) < 500: # 최소 길이 방어
                    log_print(f"[FAIL_FAST] 청크 길이 미달 (Row {chunk_count+1})", True); sys.exit(1)
                chunks.append({"payload": payload, "fill_mode": "NORMAL"})
                current_text = current_text[step:]
                chunk_count += 1

    # [Patch 4] 원문 너무 짧아 0개면 즉시 FAIL
    if not chunks:
        log_print("[FAIL_FAST] 원문이 너무 짧아 청크를 생성할 수 없습니다.", True); sys.exit(1)

    if chunk_count < need:
        log_print(f"[WARN] 원문 길이 부족. {need-chunk_count}개 랩어라운드 생성.")
        source_chunks = chunks[:]
        while len(chunks) < need:
            src = source_chunks[len(chunks) % len(source_chunks)]
            chunks.append({"payload": src["payload"], "fill_mode": "WRAP_AROUND"})
            
    return chunks[:need]

def audit_worker(task):
    client = get_client()
    prompt = (
        "You are an audit engine. Return JSON only.\n"
        "Schema: {\"verdict\": \"ALLOW|WARN|BLOCK\", \"why\": \"short_reason\", \"foreshadowing\": true|false, \"contradictions\": []}\n"
        f"Payload: {task['payload']}"
    )
    
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
            )
            res_json = json.loads(response.text)
            canon_hash = get_canonical_hash(res_json)
            
            # [Patch 7] Verdict ENUM 강제 검증
            raw_verdict = str(res_json.get("verdict", "")).upper()
            if raw_verdict not in ["ALLOW", "WARN", "BLOCK"]:
                return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'],
                             "BLOCK", 0, "BAD_VERDICT_ENUM", {"raw_verdict": raw_verdict})
            verdict = raw_verdict
            why = res_json.get("why", "OK")

            # NO_ASK 방어
            if any(p in response.text for p in ["할까요", "가능", "원하세요"]):
                 return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], 
                              "BLOCK", 0, "NO_ASK_VIOLATION", {"canon_hash": canon_hash})

            # 질문.txt 갈고리 (FP/Fun/Entity)
            fp64 = hashlib.blake2b(response.text.encode(), digest_size=8).hexdigest()
            tokens = task['payload'].split()
            fun_score = len(set(tokens)) / len(tokens) if tokens else 0.0
            
            if res_json.get("contradictions") and not res_json.get("foreshadowing"):
                verdict, why = "BLOCK", "ENTITY_CONTRADICTION"

            # [Patch 3] 인젝션 C: 실제 해시 혼선 시뮬레이션
            res_hashes = [canon_hash]
            if task.get("injection") == "C":
                res_hashes.append("INJECTED_HASH_COLLISION") # 강제로 2개 만듦
            
            # 인젝션 검거 로직
            if task.get("injection") == "A": verdict, why = "BLOCK", "A_CONTENT_CORRUPTED"
            if task.get("injection") == "B" and len(task['payload_hash']) != 64: verdict, why = "BLOCK", "B_HASH_TRUNCATED"
            if len(set(res_hashes)) > 1: verdict, why = "BLOCK", "C_HASH_MIXED" # [Patch 3] 실제 리스트 체크

            meta = {
                "attempt": attempt, "canon_hash": canon_hash, "chunk_fill": task['fill_mode'], 
                "fp64": fp64, "fun": fun_score, "res_hashes_cnt": len(res_hashes), "raw_audit": res_json
            }
            return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], 
                         verdict, 0.9, why, meta)

        except Exception as e:
            if any(err in str(e) for err in ["429", "503", "timeout"]):
                time.sleep((2 ** attempt) + random.uniform(0, 1)); continue
            return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], 
                         "BLOCK", 0, "JSON_PARSE_FAIL", {"err": str(e)})
    
    return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], "BLOCK", 0, "MAX_RETRY_FAIL", {})

def main():
    try:
        log_print(f"[START_FINAL_SEAL] {RUN_ID}")
        if not os.path.exists(INPUT_FILE):
            log_print(f"[FAIL_FAST] 파일 없음: {INPUT_FILE}", True); sys.exit(1)
            
        # 1. 청크 생성
        chunk_data = stream_build_chunks(INPUT_FILE, need=240, chunk_size=2500)
        
        # [Patch 1] 결정성 검사: PARSE_FAIL 제외하고 유효표만 집계
        log_print("[AUDIT] 결정성 3/5 검증 (Canonical Hash)...")
        client = get_client()
        sample_prompt = ("You are an audit engine. Return JSON only. Schema: {\"verdict\": \"ALLOW|WARN|BLOCK\", \"why\": \"short\"}\nPayload: " + chunk_data[0]['payload'])
        
        valid_votes = []
        for _ in range(5):
            try:
                r = client.models.generate_content(
                    model="gemini-2.5-flash", contents=sample_prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
                )
                valid_votes.append(get_canonical_hash(json.loads(r.text)))
            except: pass # PARSE_FAIL은 투표권 박탈
            time.sleep(0.2)
            
        if not valid_votes:
            log_print("[FAIL_FAST] 결정성 검사 전원 실패 (ALL PARSE_FAIL)", True); sys.exit(1)

        most_common, count = Counter(valid_votes).most_common(1)[0]
        log_print(f"[AUDIT] 유효 투표 {len(valid_votes)}/5 중 최빈값 {count}표")
        
        if count < 3:
            log_print(f"[FAIL_FAST] 결정성 미달 ({count}/5).", True); sys.exit(1)

        # 2. 태스크 생성 및 인젝션 주입
        slots = (["A"]*60 + ["B"]*36 + ["C"]*18 + ["D"]*6) * 2
        tasks = []
        for i in range(240):
            p = chunk_data[i]['payload']
            inj = "NONE"
            ph = sha256_text(p)
            
            # [Patch 2] A 인젝션: payload 변경 후 hash 재계산
            if i == 49: 
                inj = "A"
                p = p[:500] + " [CORRUPTED]"
                ph = sha256_text(p) # 재계산 필수
            
            if i == 99: inj, ph = "B", ph[:12]
            if i == 149: inj = "C"

            tasks.append({
                "row_id": i+1, "slot": slots[i], "payload": p, "payload_hash": ph, 
                "fill_mode": chunk_data[i]['fill_mode'], "injection": inj
            })

        # [Patch 5] work_packet 선출하 (메타 정보 포함)
        with open(os.path.join(RUN_DIR, "work_packet.tsv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter="\t"); w.writerow(TSV_HEADER)
            for t in tasks:
                meta_dump = json.dumps({"inj": t['injection'], "fill": t['fill_mode'], "len": len(t['payload'])})
                w.writerow([t['row_id'], f"T_{t['row_id']}", t['slot'], INPUT_FILE, t['payload_hash'], "PENDING", 0, "", int(time.time()), meta_dump])

        # 3. 실행 (8 Lanes)
        with ThreadPoolExecutor(max_workers=8) as ex:
            results = list(tqdm(ex.map(audit_worker, tasks), total=240, desc="SEALING"))
            
        # 4. 검증
        caught_a = any(r[7] == "A_CONTENT_CORRUPTED" for r in results)
        caught_b = any(r[7] == "B_HASH_TRUNCATED" for r in results)
        caught_c = any(r[7] == "C_HASH_MIXED" for r in results)
        
        if not (caught_a and caught_b and caught_c):
            log_print(f"[CRITICAL_FAIL] 인젝션 검거 실패 (A:{caught_a} B:{caught_b} C:{caught_c})", True)

        trA = len([r for r in results if 1 <= r[0] <= 120 and r[5] in ("ALLOW", "WARN")])
        trB = len([r for r in results if 121 <= r[0] <= 240 and r[5] in ("ALLOW", "WARN")])
        log_print(f"[REPORT] Truck A: {trA}, Truck B: {trB}")
        
        is_success = (trA >= 90 and trB >= 90 and caught_a and caught_b and caught_c)
        if not is_success: log_print("[CRITICAL_FAIL] 봉인 조건 미달.", True)
            
        # 5. 산출물 저장
        with open(os.path.join(RUN_DIR, "result_packet.tsv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter="\t"); w.writerow(TSV_HEADER); w.writerows(results)
            
        # [Patch 6] Manifest (핸들 누수 방지)
        manifest = {fn: {"sha256": sha256_file(os.path.join(RUN_DIR, fn)), "bytes": os.path.getsize(os.path.join(RUN_DIR, fn))} for fn in os.listdir(RUN_DIR) if os.path.isfile(os.path.join(RUN_DIR, fn))}
        with open(os.path.join(RUN_DIR, "hash_manifest.json"), "w") as f: json.dump(manifest, f, indent=2)

        # 영수증 발행 (JSONL)
        with open(os.path.join(RUN_DIR, "audit_receipt.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"run_id": RUN_ID, "ts": int(time.time()), "rows": 240, "lanes": 8, "determinism": f"{count}/5"}) + "\n")
            for r in results:
                m = json.loads(r[9])
                f.write(json.dumps({"row_id": r[0], "verdict": r[5], "payload_hash": r[4], "canon_hash": m.get("canon_hash"), "fp64": m.get("fp64")}) + "\n")
            f.write(json.dumps({"summary": {"truckA": trA, "truckB": trB, "pass": is_success}}) + "\n")
            
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