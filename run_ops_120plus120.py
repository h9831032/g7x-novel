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
# 코드 내 API 키 문자열 절대 금지. 환경변수 필수.
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    sys.stderr.write("[CRITICAL_FAIL] GEMINI_API_KEY 환경변수가 없습니다.\n")
    print("\033[91m[CRITICAL_FAIL] GEMINI_API_KEY 환경변수가 없습니다. 설정을 확인하십시오.\033[0m")
    input("Press Enter to exit..."); sys.exit(1)

# 2. 고정 경로 및 환경 설정
SSOT_ROOT = r"C:\g7core\g7_v1"
INPUT_FILE = r"C:\g7core\블레이드헌터.txt"
RUN_ID = f"OPS_FINAL_SEAL_{int(time.time())}"
RUN_DIR = os.path.join(SSOT_ROOT, "runs", RUN_ID)
os.makedirs(RUN_DIR, exist_ok=True)

TSV_HEADER = ["row_id", "task_id", "slot", "source_path", "payload_hash", "verdict", "score", "why", "ts", "meta"]

# 3. 로그 시스템 (stdout/stderr 분리 및 강제 플러시)
stdout_log = open(os.path.join(RUN_DIR, "stdout.txt"), "a", encoding="utf-8")
stderr_log = open(os.path.join(RUN_DIR, "stderr.txt"), "a", encoding="utf-8")

def log_print(msg, is_error=False):
    """화면 출력 및 파일 로그 동시 기록"""
    target = stderr_log if is_error else stdout_log
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{stamp}] {msg}"
    
    # 화면 출력 (에러는 빨간색)
    if is_error:
        print(f"\033[91m{msg}\033[0m")
    else:
        print(msg)
        
    # 파일 기록
    target.write(formatted_msg + "\n")
    target.flush()

# (A) Thread-local Client (8레인 독립성 보장)
thread_local = threading.local()
def get_client():
    if not hasattr(thread_local, "client"):
        thread_local.client = genai.Client(api_key=API_KEY)
    return thread_local.client

def get_canonical_hash(data_dict):
    """[결정성] JSON Canonical Hash (키 정렬, 공백 제거)"""
    canonical = json.dumps(data_dict, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def row10(row_id, task_id, slot, source_path, payload_hash, verdict, score, why, meta_dict):
    """[규격] 무조건 10필드 리스트 반환"""
    return [
        int(row_id), str(task_id), str(slot), str(source_path), str(payload_hash),
        str(verdict), round(float(score), 4), str(why), int(time.time()),
        json.dumps(meta_dict, ensure_ascii=False)
    ]

def build_chunks(full_text, need=240, target_len=2500):
    """[규격] 240개 강제 생성 (부족하면 Wrap-around)"""
    chunks = []
    text_len = len(full_text)
    
    # 원문이 너무 짧을 경우를 대비한 랩어라운드
    if text_len < target_len:
        log_print(f"[WARN] 원문 길이 부족({text_len}자). 랩어라운드 모드 활성화.")
        full_text = full_text * ((target_len // text_len) + 5)
    
    # 균등 분할 스텝 계산
    step = len(full_text) // need
    if step < 100: step = 100 # 최소 스텝 보장
    
    for i in range(need):
        start = i * step
        # 텍스트가 끝나면 다시 처음부터(Wrap-around)
        if start + target_len > len(full_text):
            remainder = full_text[start:]
            needed = target_len - len(remainder)
            payload = remainder + full_text[:needed]
            meta_fill = "WRAP_AROUND"
        else:
            payload = full_text[start:start+target_len]
            meta_fill = "NORMAL"
            
        chunks.append({"payload": payload, "fill_mode": meta_fill})
        
    return chunks[:need] # 정확히 240개 리턴

def audit_worker(task):
    """[RUNNER] 재시도(5회) + 백오프 + JSON강제 + 10필드보장"""
    client = get_client()
    
    # 프롬프트 고정 (1차 하청 규격 준수)
    prompt = (
        "You are an audit engine. Return JSON only.\n"
        "Schema: {\"verdict\": \"ALLOW|WARN|BLOCK\", \"why\": \"short_reason\"}\n"
        f"Payload: {task['payload']}"
    )
    
    for attempt in range(5):
        try:
            # [규격] JSON Mode 강제
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0
                )
            )
            res_json = json.loads(response.text)
            
            # [규격] Canonical Hash 생성
            canon_hash = get_canonical_hash(res_json)
            
            # [규격] NO_ASK 방어
            if any(p in response.text for p in ["할까요", "가능", "원하세요"]):
                 return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], 
                              "BLOCK", 0, "NO_ASK_VIOLATION", {"canon_hash": canon_hash})

            # 성공 리턴
            meta = {
                "attempt": attempt, "canon_hash": canon_hash, 
                "chunk_fill": task['fill_mode'], "raw_audit": res_json
            }
            return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], 
                         res_json.get("verdict", "ALLOW"), 0.9, res_json.get("why", "OK"), meta)

        except Exception as e:
            # [규격] 지수 백오프 + Jitter
            if any(err in str(e) for err in ["429", "503", "timeout"]):
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(sleep_time)
                continue
            
            # 파싱 실패 등 기타 에러는 즉시 리턴하지 않고 재시도 할지 결정하지만, 
            # JSON Parse Fail은 치명적이므로 여기선 BLOCK 처리 후 종료
            return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], 
                         "BLOCK", 0, "JSON_PARSE_FAIL", {"err": str(e)})
    
    return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], 
                 "BLOCK", 0, "MAX_RETRY_FAIL", {})

def main():
    try:
        log_print(f"[START_RUN] {RUN_ID} (FINAL SEAL)")
        
        # 1. 파일 확인
        if not os.path.exists(INPUT_FILE):
            log_print(f"[FAIL_FAST] 파일 없음: {INPUT_FILE}", True); sys.exit(1)
            
        with open(INPUT_FILE, "r", encoding="utf-8") as f: text = f.read()
        
        # 2. 청크 생성 (240개 강제)
        chunk_data = build_chunks(text, need=240, target_len=2500)
        
        # 3. 결정성 검사 (다수결 3/5, Canonical Hash)
        log_print("[AUDIT] 결정성 3/5 검증 (Canonical Hash)...")
        client = get_client()
        sample_p = chunk_data[0]['payload']
        sample_prompt = (
            "You are an audit engine. Return JSON only.\n"
            "Schema: {\"verdict\": \"ALLOW|WARN|BLOCK\", \"why\": \"short_reason\"}\n"
            f"Payload: {sample_p}"
        )
        
        votes = []
        for _ in range(5):
            r = client.models.generate_content(
                model="gemini-2.5-flash", contents=sample_prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
            )
            votes.append(get_canonical_hash(json.loads(r.text)))
            time.sleep(0.2)
            
        most_common, count = Counter(votes).most_common(1)[0]
        log_print(f"[AUDIT] 결정성 투표 결과: {count}/5 일치")
        
        if count < 3:
            log_print("[FAIL_FAST] 결정성 미달. 운영 불가.", True); sys.exit(1)
        
        # 4. 태스크 생성 (Truck A/B)
        slots = (["A"]*60 + ["B"]*36 + ["C"]*18 + ["D"]*6) * 2
        tasks = []
        for i in range(240):
            p = chunk_data[i]['payload']
            ph = hashlib.sha256(p.encode()).hexdigest()
            tasks.append({
                "row_id": i+1, "slot": slots[i], "payload": p, "payload_hash": ph, 
                "fill_mode": chunk_data[i]['fill_mode']
            })
            
        # 5. 실행 (8 Lanes)
        with ThreadPoolExecutor(max_workers=8) as ex:
            results = list(tqdm(ex.map(audit_worker, tasks), total=240, desc="SEALING"))
            
        # 6. 결과 검증 (Truck A/B 90개 이상)
        truck_a_pass = len([r for r in results if 1 <= r[0] <= 120 and r[5] in ("ALLOW", "WARN")])
        truck_b_pass = len([r for r in results if 121 <= r[0] <= 240 and r[5] in ("ALLOW", "WARN")])
        
        log_print(f"[REPORT] Truck A: {truck_a_pass}/120, Truck B: {truck_b_pass}/120")
        
        is_success = True
        if truck_a_pass < 90 or truck_b_pass < 90:
            log_print("[CRITICAL_FAIL] 트럭별 최소 생산량(90) 미달.", True)
            is_success = False # 파일은 남기되 성공 판정은 안 함
            
        # 7. 산출물 저장 (TSV 10필드)
        with open(os.path.join(RUN_DIR, "result_packet.tsv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter="\t"); w.writerow(TSV_HEADER); w.writerows(results)
            
        # 8. 영수증 발행 (Real JSONL Format)
        receipt_path = os.path.join(RUN_DIR, "audit_receipt.jsonl")
        with open(receipt_path, "w", encoding="utf-8") as f:
            # Header
            header = {
                "run_id": RUN_ID, "ts": int(time.time()), "rows": 240, "lanes": 8, 
                "determinism_vote": f"{count}/5", "model": "gemini-2.5-flash"
            }
            f.write(json.dumps(header) + "\n")
            
            # Body (Rows)
            for r in results:
                row_meta = json.loads(r[9])
                row_receipt = {
                    "row_id": r[0], "verdict": r[5], "payload_hash": r[4], 
                    "canon_hash": row_meta.get("canon_hash"), "fill_mode": row_meta.get("chunk_fill")
                }
                f.write(json.dumps(row_receipt) + "\n")
                
            # Footer
            footer = {
                "summary": {
                    "truckA_real": truck_a_pass, "truckB_real": truck_b_pass, 
                    "pass": is_success
                }
            }
            f.write(json.dumps(footer) + "\n")
            
        # 9. 최종 판정
        if not is_success:
            log_print("[FAIL] 봉인 실패 (트럭 품질 미달). 로그를 확인하십시오.", True)
            sys.exit(1)
        else:
            log_print(f"[SUCCESS] 봉인 완료: {RUN_DIR}")

    except Exception as e:
        log_print(f"[CRITICAL_ERROR] {str(e)}", True)
        sys.exit(1)
        
    finally:
        stdout_log.close(); stderr_log.close()
        # [PERSISTENCE_GUARD]
        print("\n" + "="*60)
        input("Audit Done. 엔터를 누르면 창이 닫힙니다.")

if __name__ == "__main__":
    main()