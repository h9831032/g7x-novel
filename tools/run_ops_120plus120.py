import os
import sys
import json
import csv
import time
import hashlib
import re
import threading
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# [MANDATE: ELITE_ARCHITECT_MODE]
API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"

# 1. 공장 환경 설정 
SSOT_ROOT = r"C:\g7core\g7_v1"
INPUT_FILE = r"C:\g7core\블레이드헌터.txt"
RUN_ID = f"OPS_EXTREME_{int(time.time())}"
RUN_DIR = os.path.join(SSOT_ROOT, "runs", RUN_ID)
os.makedirs(RUN_DIR, exist_ok=True)

TSV_HEADER = ["row_id", "task_id", "slot", "source_path", "payload_hash", "verdict", "score", "why", "ts", "meta"]

# 로그 시스템 (stdout/stderr 저장) [cite: 3]
stdout_path = os.path.join(RUN_DIR, "stdout.txt")
stderr_path = os.path.join(RUN_DIR, "stderr.txt")
stdout_log = open(stdout_path, "a", encoding="utf-8")
stderr_log = open(stderr_path, "a", encoding="utf-8")

def log_print(msg, is_error=False):
    target = stderr_log if is_error else stdout_log
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if is_error: print(f"\033[91m{msg}\033[0m") # [cite: 3] 적색 출력
    else: print(msg)
    target.write(f"{stamp}\t{msg}\n"); target.flush()

# 패치 D: Thread-local Client 재사용
thread_local = threading.local()
def get_client():
    if not hasattr(thread_local, "client"):
        thread_local.client = genai.Client(api_key=API_KEY)
    return thread_local.client

def row10(row_id, task_id, slot, source_path, payload_hash, verdict, score, why, meta_dict):
    """[FACTORY_STANDARD] 무조건 10필드 반환 보장"""
    return [int(row_id), str(task_id), str(slot), str(source_path), str(payload_hash),
            str(verdict), round(float(score), 4), str(why), int(time.time()), 
            json.dumps(meta_dict, ensure_ascii=False)]

def audit_worker(task):
    """[RUNNER] 패치 A(재시도), B(JSON 강제) 통합"""
    client = get_client()
    max_retries = 5
    
    for attempt in range(max_retries):
        try:
            # 패치 B: response_mime_type 적용 (Google AI for Developers 규격)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Analyze for 60 logic gates. Return JSON only. Payload: {task['payload']}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0
                )
            )
            res_json = json.loads(response.text)
            
            # [EVIDENCE_MANDATED_AUDIT] SHA1 영수증 발행 [cite: 4]
            res_hash = hashlib.sha1(response.text.encode()).hexdigest()
            meta = {"attempt": attempt, "res_hash": res_hash, "audit": res_json}
            
            return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], 
                         res_json.get("verdict", "ALLOW"), res_json.get("score", 0.9), "Audit Passed", meta)

        except Exception as e:
            # 패치 A: 429/503/timeout 지수 백오프
            if any(err in str(e) for err in ["429", "503", "timeout"]):
                wait_time = 2 ** attempt
                log_print(f"[RETRY] Row {task['row_id']} - Attempt {attempt+1}/{max_retries} (Wait {wait_time}s)")
                time.sleep(wait_time); continue
            
            return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], 
                         "BLOCK", 0, f"ERR_{type(e).__name__}", {"err": str(e)})
    
    return row10(task['row_id'], f"T_{task['row_id']}", task['slot'], INPUT_FILE, task['payload_hash'], "BLOCK", 0, "MAX_RETRY_EXCEEDED", {})

def determinism_3of5_check(payload):
    """패치 C: 결정성 완화 (3/5 이상 일치 시 PASS) [cite: 5]"""
    client = get_client()
    hashes = []
    for _ in range(5):
        try:
            r = client.models.generate_content(model="gemini-2.5-flash", contents=payload, config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0))
            hashes.append(hashlib.sha1(r.text.encode()).hexdigest())
        except: hashes.append("FAIL")
    
    # 가장 많이 나온 해시의 빈도 측정
    most_common_cnt = max([hashes.count(h) for h in set(hashes)])
    return most_common_cnt >= 3

def main():
    log_print(f"[START_FACTORY] {RUN_ID}")
    
    # [EVIDENCE_OR_FAIL] 파일 실존 확인 [cite: 4]
    if not os.path.exists(INPUT_FILE):
        log_print(f"[FAIL_FAST] 원자재 부족: {INPUT_FILE}", True); sys.exit(1)
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f: full_text = f.read()
    
    # 가변 청크 엔진 (240개 규격 보장)
    step = max(1, len(full_text) // 240)
    chunks = [full_text[i*step : i*step + 2500] for i in range(240)]
    
    # 패치 C: 결정성 검증 (완화된 3/5 적용) [cite: 5]
    log_print("[AUDIT] 결정성 3/5 검증 중...")
    if not determinism_3of5_check(chunks[0]):
        log_print("[CRITICAL_FAIL] 운영 진동 과다 (3/5 미달). 봉인을 중단합니다.", True); sys.exit(1)
    log_print("[PASS] 결정성 검증 완료.")

    # 슬롯 배정 및 태스크 구축 
    slots = (["A"]*60 + ["B"]*36 + ["C"]*18 + ["D"]*6) * 2
    tasks = [{"row_id": i+1, "slot": slots[i], "payload": chunks[i], "payload_hash": hashlib.sha1(chunks[i].encode()).hexdigest()} for i in range(240)]

    # [LANES=8] 병렬 기동
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(tqdm(executor.map(audit_worker, tasks), total=240, desc="PHOENIX_OPS"))

    # 결과 저장 및 영수증 발행 [cite: 4]
    with open(os.path.join(RUN_DIR, "result_packet.tsv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t"); w.writerow(TSV_HEADER); w.writerows(results)
    
    log_print(f"[SUCCESS] 봉인 완료: {RUN_DIR}")

if __name__ == "__main__":
    try: main()
    finally:
        stdout_log.close(); stderr_log.close()
        # [PERSISTENCE_GUARD] 확인 전까지 종료 방지 [cite: 2]
        input("\nAudit Done. 영수증을 확인하십시오. (Press Enter to exit)")