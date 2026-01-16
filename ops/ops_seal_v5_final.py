import os, sys, json, csv, time, hashlib, threading, io, glob
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# [PATCH-0] UTF-8 및 윈도우 환경 방어
sys.stdin = io.TextIOWrapper(sys.stdin.detach(), encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

# [MANDATE] SSOT 설정 및 경로 고정
API_KEY = os.getenv("GEMINI_API_KEY")
SSOT_ROOT = r"C:\g7core\g7_v1"
INPUT_CHUNKS = r"C:\g6core\g6_v24\data\umr\chunks"

# [하청-②] 드리프트 센티넬 고정 (샘플링 금지)
DRIFT_SENTINELS = [1, 7, 13, 21, 34, 55, 89, 120, 180, 240]

all_files = glob.glob(os.path.join(INPUT_CHUNKS, "*"))
INPUT_FILE = max(all_files, key=os.path.getsize)
RUN_ID = f"FINAL_SEAL_V5_{int(time.time())}"
RUN_DIR = os.path.join(SSOT_ROOT, "runs", RUN_ID)
os.makedirs(RUN_DIR, exist_ok=True)

# [하청-④] 실행 구조 고정 (8 Lanes / 4 Concurrent)
MAX_WORKERS = 8
SEMAPHORE_LIMIT = 4
GEMINI_SEM = threading.Semaphore(SEMAPHORE_LIMIT) 
SAVE_LOCK = threading.Lock()
DRIFT_CNT = 0

def get_canonical_hash(res_dict):
    """결정성 검증을 위한 정규화 해시 생성"""
    normalized = json.dumps(res_dict, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def audit_worker(task):
    global DRIFT_CNT
    client = genai.Client(api_key=API_KEY)
    config = types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
    prompt = f"Mode: AUDIT. JSON ONLY. Payload: {task['payload']}"

    try:
        with GEMINI_SEM:
            # 1차 호출
            r1 = client.models.generate_content(model="gemini-2.5-flash", contents=prompt, config=config)
            res1 = json.loads(r1.text)
            h1 = get_canonical_hash(res1)
            
            # [하청-②] 센티넬 구역 재현성 무조건 검증
            drift_occurred = False
            if task['row_id'] in DRIFT_SENTINELS:
                r2 = client.models.generate_content(model="gemini-2.5-flash", contents=prompt, config=config)
                h2 = get_canonical_hash(json.loads(r2.text))
                if h1 != h2:
                    with SAVE_LOCK: DRIFT_CNT += 1
                    drift_occurred = True

        # [하청-③] audit_receipt.jsonl 기록
        with SAVE_LOCK:
            with open(os.path.join(RUN_DIR, "audit_receipt.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps({"id": task['row_id'], "h": h1, "drift": drift_occurred}, ensure_ascii=False) + "\n")
        
        return {"ok": True, "id": task['row_id'], "verdict": res1.get("verdict", "BLOCK")}
    except Exception as e:
        return {"ok": False, "id": task['row_id'], "error": str(e)}

def main():
    print(f"\n[V5-SEAL START] 8 lanes / 4 concurrent calls")
    print(f"Target: {os.path.basename(INPUT_FILE)}")
    
    # [하청-②] 실청크 240개 적재
    tasks = []
    with open(INPUT_FILE, "r", encoding="utf-8", errors="replace") as f:
        for i in range(240):
            line = f.readline()
            if not line: break
            tasks.append({"row_id": i+1, "payload": line[:2500]})

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        results = list(tqdm(ex.map(audit_worker, tasks), total=len(tasks), desc="[SEALING]"))

    # [하청-①] 성공 조건 단일화 (흑백 판정)
    failed_cnt = sum(1 for r in results if not r['ok'])
    pass_op = (failed_cnt == 0)
    # 1건이라도 드리프트 발생 시 FAIL
    pass_seal = (pass_op and DRIFT_CNT == 0)

    # [하청-③] 증거팩 강제 생성
    report = {
        "pass_op": pass_op,
        "pass_seal": pass_seal,
        "drift_cnt": DRIFT_CNT,
        "sentinels_checked": DRIFT_SENTINELS,
        "structure": "8 lanes / 4 concurrent calls",
        "exitcode": 0 if pass_seal else 2
    }
    
    # 1. verify_report.json
    with open(os.path.join(RUN_DIR, "verify_report.json"), "w") as f: json.dump(report, f, indent=2)
    # 2. exitcode.txt
    with open(os.path.join(RUN_DIR, "exitcode.txt"), "w") as f: f.write(str(report['exitcode']))
    # 3. hash_manifest.json (단순화)
    with open(os.path.join(RUN_DIR, "hash_manifest.json"), "w") as f:
        json.dump({"report_hash": hashlib.sha256(json.dumps(report).encode()).hexdigest()}, f)

    print(f"\n[FINAL] Drift: {DRIFT_CNT} | Pass: {pass_seal} | ExitCode: {report['exitcode']}")
    sys.exit(report['exitcode'])

if __name__ == "__main__":
    main()