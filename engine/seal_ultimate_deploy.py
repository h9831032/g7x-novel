import os, sys, json, hashlib, time, threading, shutil, random
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# [MANDATE-0] API_KEY 환경변수 우선 적용 (보안/운영)
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY")
SSOT_ROOT = r"C:\g7core\g7_v1"
INPUT_PATH = r"C:\g6core\g6_v24\data\umr\chunks\fantasy_chunks.jsonl"

# [MANDATE-1] 타임스탬프 기반 RUN_DIR 분리 (회귀/증거 보존)
TIMESTAMP = time.strftime("%Y%m%d_%H%M%S")
RUN_DIR = os.path.join(SSOT_ROOT, "runs", f"SEAL_RUN_{TIMESTAMP}")
os.makedirs(RUN_DIR, exist_ok=True)

# [C1] stdout.txt 캡처 (DualLogger)
class DualLogger(object):
    def __init__(self, run_dir):
        self.terminal = sys.stdout
        self.log = open(os.path.join(run_dir, "stdout.txt"), "w", encoding="utf-8")
    def write(self, message):
        self.terminal.write(message); self.log.write(message)
    def flush(self):
        self.terminal.flush(); self.log.flush()

sys.stdout = DualLogger(RUN_DIR)

# [MANDATE-4] 고정 24개 + 랜덤 24개 (총 48개 보초병 세우기)
FIXED_SENTINELS = [1, 7, 13, 21, 34, 55, 60, 61, 73, 89, 97, 101, 109, 113, 120, 123, 137, 144, 177, 199, 210, 222, 235, 240]
RANDOM_SENTINELS = random.sample([i for i in range(1, 241) if i not in FIXED_SENTINELS], 24)
ALL_SENTINELS = set(FIXED_SENTINELS + RANDOM_SENTINELS)

thread_local = threading.local()
def get_client():
    if not hasattr(thread_local, "client"):
        thread_local.client = genai.Client(api_key=API_KEY)
    return thread_local.client

def get_res(p):
    client = get_client()
    config = types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
    prompt = "Return JSON only. Schema: {\"verdict\":\"ALLOW|BLOCK\",\"why\":\"short\"}\nPayload: " + p
    r = client.models.generate_content(model="gemini-2.5-flash", contents=prompt, config=config)
    j = json.loads(r.text)
    v = j.get("verdict", "BLOCK")
    if v not in ["ALLOW", "BLOCK"]: v = "BLOCK"
    return v, hashlib.sha256(v.encode()).hexdigest()

def seal_worker(task):
    row_id, p = task['id'], task['p']
    v1, v_h1 = get_res(p)
    v_drift, v_resolved, v_final, v_h_final = False, False, v1, v_h1
    votes = [v1]

    # [MANDATE-3] 다수결 용접 (Voting)
    if row_id in ALL_SENTINELS:
        v2, v_h2 = get_res(p)
        if v_h1 != v_h2:
            votes = [v1, v2]
            for _ in range(3):
                vn, _ = get_res(p); votes.append(vn)
            v_counts = {v: votes.count(v) for v in set(votes)}
            v_final = max(v_counts, key=v_counts.get)
            if v_counts[v_final] >= 4:
                v_resolved, v_drift = True, False
                v_h_final = hashlib.sha256(v_final.encode()).hexdigest()
            else: v_drift = True
    return {"ok": True, "res": {"row": row_id, "v": v_final, "v_h": v_h_final, "v_drift": v_drift, "resolved": v_resolved, "votes": votes}}

def main():
    print(f"\n" + "="*60 + f"\n [!] MANDATE: V8_DEPLOY_READY (Random Sentinel + TS)\n" + "="*60)
    print(f" [@] RUN_DIR: {RUN_DIR}")
    print(f" [@] SENTINELS: Fixed 24 + Random 24 = {len(ALL_SENTINELS)} active")
    
    chunks = []
    with open(INPUT_PATH, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if len(line.strip()) >= 500: chunks.append(line.strip())
            if len(chunks) >= 240: break

    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(tqdm(ex.map(lambda i: seal_worker({"id": i+1, "p": chunks[i]}), range(240)), total=240))

    res_list = [r["res"] for r in results if r["ok"]]
    
    # 1. audit_receipt.jsonl (명세서)
    receipt_path = os.path.join(RUN_DIR, "audit_receipt.jsonl")
    with open(receipt_path, "w", encoding="utf-8") as f:
        for r in res_list: f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 2. verify_report.json (보고서)
    rw_a, rw_b = len(res_list[:120]), len(res_list[120:])
    v_drift_cnt = sum(1 for r in res_list if r["v_drift"])
    pass_seal = (rw_a >= 90 and rw_b >= 90 and v_drift_cnt == 0)
    with open(os.path.join(RUN_DIR, "verify_report.json"), "w") as f:
        json.dump({"pass_seal": pass_seal, "drift_fail_cnt": v_drift_cnt, "truck_rw": {"A": rw_a, "B": rw_b}, "run_ts": TIMESTAMP}, f, indent=2)

    with open(os.path.join(RUN_DIR, "exitcode.txt"), "w") as f: f.write("0" if pass_seal else "2")

    sys.stdout.flush()

    # 3. hash_manifest.json (쇠사슬 묶기 - 4종 세트)
    manifest = {}
    for fn in ["verify_report.json", "audit_receipt.jsonl", "exitcode.txt", "stdout.txt"]:
        p = os.path.join(RUN_DIR, fn)
        if os.path.exists(p):
            with open(p, "rb") as f: manifest[fn] = hashlib.sha256(f.read()).hexdigest()
    
    with open(os.path.join(RUN_DIR, "hash_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n[@] DEPLOY_READY_RUN COMPLETE. PASS={pass_seal}")
    sys.exit(0 if pass_seal else 2)

if __name__ == "__main__": main()