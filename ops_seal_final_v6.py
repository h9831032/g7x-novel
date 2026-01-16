import os, sys, json, csv, time, hashlib, threading, io, glob, shutil
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# [MANDATE-0] API_KEY & 경로 (형님 오더 박제)
API_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
SSOT_ROOT = r"C:\g7core\g7_v1"
INPUT_DIR = r"C:\g6core\g6_v24\data\umr\chunks"
TARGET_FILES = ["fantasy_chunks.jsonl", "economy_chunks.jsonl"]

# [MANDATE-CLEAN] 이전 기록 삭제 및 폴더 초기화 (신용 회복 핵심)
RUN_DIR = os.path.join(SSOT_ROOT, "runs", "FINAL_CLEAN_SESSION")
if os.path.exists(RUN_DIR):
    shutil.rmtree(RUN_DIR)  # 기존 85개 찌꺼기 물리적 삭제
os.makedirs(RUN_DIR, exist_ok=True)

# [C1-대응] 시각성 확보: 화면 출력 유지 + 파일 동시 기록 (DualLogger)
class DualLogger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(os.path.join(RUN_DIR, "stdout.txt"), "w", encoding="utf-8")
        self.err = open(os.path.join(RUN_DIR, "stderr.txt"), "w", encoding="utf-8")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = DualLogger()

# [M3] OPS 헌법 규격 (120+120 / RW 90)
POLICY = {
    "TRUCK_SIZE": 120, "RW_LIMIT": 90,
    "SENTINELS": [1, 7, 13, 21, 34, 55, 60, 61, 73, 89, 97, 101, 109, 113, 120, 3, 17, 44, 77, 99],
    "SCHEMA": '{"verdict":"ALLOW|WARN|BLOCK","why":"short"}',
    "MODEL": "gemini-2.5-flash", "TEMP": 0
}
POLICY_HASH = hashlib.sha256(json.dumps(POLICY, sort_keys=True).encode()).hexdigest()

DRIFT_TOTAL = 0
SAVE_LOCK = threading.Lock()
GEMINI_SEM = threading.Semaphore(4) # 워커 4 고정

def audit_worker(task):
    global DRIFT_TOTAL
    client = genai.Client(api_key=API_KEY)
    config = types.GenerateContentConfig(response_mime_type="application/json", temperature=POLICY["TEMP"])
    prompt = f"Return JSON only. Schema: {POLICY['SCHEMA']}\nPayload: {task['p']}"

    try:
        with GEMINI_SEM:
            r1 = client.models.generate_content(model=POLICY["MODEL"], contents=prompt, config=config)
            res1 = json.loads(r1.text)
            h1 = hashlib.sha256(f"{res1['verdict']}{res1.get('why','')[:50]}".encode()).hexdigest()
            
            is_drift = False
            slot = ((task['id'] - 1) % POLICY["TRUCK_SIZE"]) + 1
            if slot in POLICY["SENTINELS"]:
                r2 = client.models.generate_content(model=POLICY["MODEL"], contents=prompt, config=config)
                h2 = hashlib.sha256(f"{json.loads(r2.text)['verdict']}{json.loads(r2.text).get('why','')[:50]}".encode()).hexdigest()
                if h1 != h2:
                    with SAVE_LOCK: DRIFT_TOTAL += 1
                    is_drift = True
                    print(f"\n[FAIL_FAST] DRIFT DETECTED at Row {task['id']}")

        # [EVIDENCE-1] audit_receipt.jsonl (개별 영수증)
        receipt = {"p_hash": POLICY_HASH, "row": task['id'], "h": h1, "v": res1.get("verdict"), "d": is_drift}
        RECEIPT_PATH = os.path.join(RUN_DIR, "audit_receipt.jsonl")
        with SAVE_LOCK:
            with open(RECEIPT_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(receipt, ensure_ascii=False) + "\n")
            # [EVIDENCE-2] result_packet.tsv (정밀 데이터팩)
            with open(os.path.join(RUN_DIR, "result_packet.tsv"), "a", newline="", encoding="utf-8") as f:
                csv.writer(f, delimiter="\t").writerow([task['id'], True, res1.get("verdict"), h1, is_drift])
        return {"ok": True, "v": res1.get("verdict"), "d": is_drift}
    except Exception as e:
        return {"ok": False, "v": "ERROR", "err": str(e)}

def main():
    print(f"\n" + "="*60)
    print(f" [MANDATE] CLEAN_START: PREVIOUS DATA PURGED")
    print(f" [POLICY] HASH: {POLICY_HASH}")
    print(f" [TARGET] {TARGET_FILES}")
    print("="*60 + "\n")
    
    # [FAST-SCAN] 2.3GB 병목 제거 로직
    chunks = []
    for fn in TARGET_FILES:
        fp = os.path.join(INPUT_DIR, fn)
        if os.path.exists(fp):
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                while len(chunks) < 240:
                    data = f.read(10000)
                    if not data: break
                    for l in data.split('\n'):
                        if len(l.strip()) >= 500:
                            chunks.append(l.strip())
                            if len(chunks) >= 240: break

    # [THREADING] 워커 4 주행
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(tqdm(ex.map(lambda i: audit_worker({"id": i+1, "p": chunks[i]}), range(240)), 
                           total=240, desc="NEW_SEALING", unit="chunk", colour="red"))

    # [M3] OPS 헌법 판정 (RW >= 90)
    res_a = results[:120]
    res_b = results[120:]
    rw_a = sum(1 for r in res_a if r['ok'] and r['v'] in ["ALLOW", "WARN"])
    rw_b = sum(1 for r in res_b if r['ok'] and r['v'] in ["ALLOW", "WARN"])
    
    pass_seal = (rw_a >= POLICY["RW_LIMIT"] and rw_b >= POLICY["RW_LIMIT"] and DRIFT_TOTAL == 0)
    exit_code = 0 if pass_seal else 2

    # [EVIDENCE-3] exitcode.txt
    with open(os.path.join(RUN_DIR, "exitcode.txt"), "w") as f: f.write(str(exit_code))
    
    # [EVIDENCE-4] verify_report.json
    report = {"p_hash": POLICY_HASH, "pass_seal": pass_seal, "drift_total": DRIFT_TOTAL, "truck_rw": {"A": rw_a, "B": rw_b}}
    with open(os.path.join(RUN_DIR, "verify_report.json"), "w") as f: json.dump(report, f, indent=2)
    
    # [EVIDENCE-5] hash_manifest.json (전체 파일 무결성 검증)
    manifest = {}
    for fn in ["stdout.txt", "audit_receipt.jsonl", "result_packet.tsv", "verify_report.json", "exitcode.txt"]:
        p = os.path.join(RUN_DIR, fn)
        if os.path.exists(p):
            manifest[fn] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    with open(os.path.join(RUN_DIR, "hash_manifest.json"), "w") as f: json.dump(manifest, f, indent=2)

    print(f"\n" + "="*60)
    print(f" [FINAL_RESULT] ExitCode: {exit_code}")
    print(f" [SUMMARY] Drift: {DRIFT_TOTAL} | Truck-A: {rw_a}/120 | Truck-B: {rw_b}/120")
    print(f" [RECEIPT] ALL EVIDENCE SAVED IN {RUN_DIR}")
    print("="*60 + "\n")
    
    # [PERSISTENCE_GUARD] [2026-01-03]
    input(" [Audit Done] Press Enter to Exit...")

if __name__ == "__main__":
    main()