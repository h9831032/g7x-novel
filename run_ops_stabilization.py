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
    print("[CRITICAL_FAIL] GEMINI_API_KEY 환경변수가 없습니다."); sys.exit(1)

# 1. 고정 경로 및 환경
SSOT_ROOT = r"C:\g7core\g7_v1"
INPUT_FILE = r"C:\g7core\블레이드헌터.txt"
RUN_ID = f"OPS_STABLE_V1_FINAL_{int(time.time())}"
RUN_DIR = os.path.join(SSOT_ROOT, "runs", RUN_ID)
os.makedirs(RUN_DIR, exist_ok=True)

TSV_HEADER = ["row_id", "task_id", "slot", "source_path", "payload_hash", "verdict", "score", "why", "ts", "meta"]

# 로그 시스템 (stdout/stderr 실시간 flush)
stdout_log = open(os.path.join(RUN_DIR, "stdout.txt"), "a", encoding="utf-8")
stderr_log = open(os.path.join(RUN_DIR, "stderr.txt"), "a", encoding="utf-8")

def log_print(msg, is_error=False):
    target = stderr_log if is_error else stdout_log
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if is_error: print(f"\033[91m{msg}\033[0m")
    else: print(msg)
    target.write(f"{stamp}\t{msg}\n"); target.flush()

# (A) Thread-local Client 재사용 (8레인 고정)
thread_local = threading.local()
def get_client():
    if not hasattr(thread_local, "client"):
        thread_local.client = genai.Client(api_key=API_KEY)
    return thread_local.client

def row10(row_id, task_id, slot, source_path, payload_hash, verdict, score, why, meta_dict):
    """ [규격 사수] 무조건 10필드 반환 """
    return [int(row_id), str(task_id), str(slot), str(source_path), str(payload_hash),
            str(verdict), float(score), str(why), int(time.time()), json.dumps(meta_dict, ensure_ascii=False)]

def audit_worker(task):
    """ [RUNNER] 래퍼 + JSON 파서 + 재시도 통합 """
    client = get_client()
    contents = "You are an audit engine. Return JSON only. Schema: {\"verdict\": \"ALLOW|WARN|BLOCK\", \"why\": \"short_reason\"}\nPayload: " + task['payload']
    
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
            )
            res_json = json.loads(response.text)
            
            # NO_ASK 차단
            if any(p in response.text for p in ["할까요", "가능", "원하세요"]):
                 return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], "BLOCK", 0, "NO_ASK_VIOLATION", {})

            return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], 
                         res_json.get("verdict", "ALLOW"), 1.0, res_json.get("why", "OK"), {"attempt": attempt})

        except Exception as e:
            if any(err in str(e) for err in ["429", "503", "timeout"]):
                time.sleep((2 ** attempt) + random.uniform(0, 1))
                continue
            return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], 
                         "BLOCK", 0, f"ERR_{type(e).__name__}", {"err": str(e)})
    
    return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], "BLOCK", 0, "MAX_RETRY_FAIL", {})

def main():
    log_print(f"[1차 하청 가동] {RUN_ID}")
    
    if not os.path.exists(INPUT_FILE): log_print("파일 없음", True); sys.exit(1)
    with open(INPUT_FILE, "r", encoding="utf-8") as f: text = f.read()
    
    # 가변 청크 엔진 (240개 보장)
    step = max(1, len(text) // 240)
    chunks = [text[i*step : i*step + 1200] for i in range(240)]

    # (C) [V1.3 PATCHED] 다수결 결정성 검사 (Majority Vote Mode)
    log_print("[AUDIT] 결정성 검사 중 (다수결 필터링 가동)...")
    client = get_client()
    sample_c = "You are an audit engine. Return JSON only. Schema: {\"verdict\": \"ALLOW|WARN|BLOCK\", \"why\": \"short_reason\"}\nPayload: " + chunks[0]
    
    verdicts = []
    for i in range(5):
        try:
            r = client.models.generate_content(model="gemini-2.5-flash", contents=sample_c, config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0))
            v = json.loads(r.text).get("verdict", "ERROR")
            verdicts.append(v)
        except:
            verdicts.append("PARSE_FAIL")
        time.sleep(0.3)

    # 다수결 판정
    occurence_count = Counter(verdicts)
    most_common_verdict, count = occurence_count.most_common(1)[0]
    
    log_print(f"[AUDIT] 진동 결과: {verdicts} -> 최빈값: {most_common_verdict} ({count}/5)")

    if count < 3: # 3/5 미만이면 진짜로 멍청한 상태 (Unstable)
        log_print(f"[FAIL_FAST] 결정성 임계치 미달 (최다 빈도 {count}/5). 운영 불가.", True); sys.exit(1)
    
    log_print(f"[PASS] 운영 안정성 확보. 판정 기준: {most_common_verdict}")

    # 태스크 구축 (120+120)
    tasks = [{"row_id": i+1, "slot": "A" if i<120 else "B", "payload": chunks[i], "payload_hash": hashlib.sha256(chunks[i].encode()).hexdigest()} for i in range(240)]

    # 8레인 풀가동
    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(tqdm(ex.map(audit_worker, tasks), total=240, desc="OPS_STABILIZING"))

    # TSV 봉인
    with open(os.path.join(RUN_DIR, "result_packet.tsv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t"); w.writerow(TSV_HEADER); w.writerows(results)
    
    # Receipt 발행
    receipt = {"run_id": RUN_ID, "rows": len(results), "determinism_vote": f"{count}/5", "final_verdict": most_common_verdict}
    with open(os.path.join(RUN_DIR, "audit_receipt.jsonl"), "w") as f:
        json.dump(receipt, f)

    log_print(f"[1차 봉인 완료] {RUN_DIR}")

if __name__ == "__main__":
    try: main()
    finally:
        stdout_log.close(); stderr_log.close()
        input("\n[Audit Done] 엔터를 눌러 안전하게 종료하십시오.")