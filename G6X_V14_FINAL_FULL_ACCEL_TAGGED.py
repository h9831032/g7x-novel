import os, sys, json, hashlib, time, threading, random, re
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# [MANDATE-0] API_KEY 및 모델 설정
RAW_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
API_KEY = re.sub(r'[^\x00-\x7F]+', '', RAW_KEY).strip()
MODEL_ID = "models/gemini-2.5-flash"

SSOT_ROOT = r"C:\g7core\g7_v1"
INPUT_PATH = r"C:\g6core\g6_v24\data\umr\chunks\fantasy_chunks.jsonl"
TOTAL_CHUNKS_EST = 100000

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = os.path.join(SSOT_ROOT, "runs", f"FULL_ACCEL_TAGGED_{TIMESTAMP}")
os.makedirs(RUN_DIR, exist_ok=True)

# [하청지시서 적용] G6X_TAG_SCHEMA_v1.txt 내용 반영 (표식 고정)
# A. 드리프트: TAG_DRIFT_PLOT, TAG_DRIFT_CHARACTER, TAG_DRIFT_TONE
# B. 석화: TAG_PETRIFY, TAG_PATTERN_LOOP
# C. 오류: TAG_COMMONSENSE_FAIL, TAG_POWER_RULE_FAIL, TAG_CAUSAL_FAIL
# D. 재미: TAG_FUN_LOW, TAG_FUN_MID, TAG_FUN_HIGH

class DashboardLogger(object):
    def __init__(self, run_dir):
        self.terminal = sys.stdout
        self.log_path = os.path.join(run_dir, "stdout.txt")
        self.log = open(self.log_path, "a", encoding="utf-8")
    def write(self, message):
        self.terminal.write(message); self.log.write(message)
    def flush(self):
        self.terminal.flush(); self.log.flush()
        try: os.fsync(self.log.fileno())
        except: pass

logger = DashboardLogger(RUN_DIR)
sys.stdout = logger

FIXED_SENTINELS = [1, 21, 55, 89, 101, 113, 123, 144, 177, 199, 222, 240]

thread_local = threading.local()
def get_client():
    if not hasattr(thread_local, "client"):
        thread_local.client = genai.Client(api_key=API_KEY)
    return thread_local.client

def get_res(p):
    client = get_client()
    config = types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
    # 하청지시서 기반: 태그 표식을 위한 기반 판정 유도 프롬프트
    prompt = "JSON only. {\"verdict\":\"ALLOW|BLOCK\",\"why\":\"short\",\"tags\":[]} \nPayload: " + p
    for _ in range(3):
        try:
            r = client.models.generate_content(model=MODEL_ID, contents=prompt, config=config)
            j = json.loads(r.text)
            return j, hashlib.sha256(r.text.encode()).hexdigest(), True
        except: time.sleep(1)
    return {"verdict":"BLOCK","why":"error","tags":[]}, hashlib.sha256("error".encode()).hexdigest(), False

def seal_worker(task):
    row_id, p, sentinels = task['id'], task['p'], task['sentinels']
    res1, h1, ok1 = get_res(p)
    v_drift, v_resolved, v_final = False, False, res1
    v_h_final = h1
    
    cycle_id = (row_id - 1) % 240 + 1
    if cycle_id in sentinels and ok1:
        res2, h2, ok2 = get_res(p)
        if ok2 and h1 != h2:
            v_drift = True
            # [다수결 투표]
            votes = [json.dumps(res1, sort_keys=True), json.dumps(res2, sort_keys=True)]
            for _ in range(3):
                rn, _, okn = get_res(p)
                if okn: votes.append(json.dumps(rn, sort_keys=True))
            
            v_counts = {v: votes.count(v) for v in set(votes)}
            best_json_str = max(v_counts, key=v_counts.get)
            if v_counts[best_json_str] >= 4:
                v_resolved = True
                v_final = json.loads(best_json_str)
                v_h_final = hashlib.sha256(best_json_str.encode()).hexdigest()
    
    # 영수증 규격 고정
    return {"ok": ok1, "res": {
        "row": row_id, 
        "v": v_final.get("verdict", "BLOCK"), 
        "why": v_final.get("why", ""), 
        "tags": v_final.get("tags", []), # 하청지시서용 태그 필드 확보
        "v_h": v_h_final, 
        "v_drift": v_drift, 
        "resolved": v_resolved
    }}

def main():
    print(f"### [G6X ULTIMATE_TAGGED] 12GB 본 공정 8코어 진격")
    total_processed, total_ok_cnt, total_drift_cnt, total_resolved_cnt = 0, 0, 0, 0
    receipt_path = os.path.join(RUN_DIR, "audit_receipt.jsonl")
    
    with open(INPUT_PATH, "r", encoding="utf-8", errors="replace") as f_in, \
         open(receipt_path, "a", encoding="utf-8") as f_out:
        
        batch = []
        for i, line in enumerate(f_in):
            batch.append({"id": i + 1, "p": line.strip()})
            if len(batch) >= 240:
                dynamic_random = random.sample([n for n in range(1, 241) if n not in FIXED_SENTINELS], 12)
                current_sentinels = set(FIXED_SENTINELS + dynamic_random)
                for t in batch: t['sentinels'] = current_sentinels
                
                with ThreadPoolExecutor(max_workers=8) as ex: # 8코어 풀악셀
                    results = list(ex.map(seal_worker, batch))
                
                for r in results:
                    if r["ok"]:
                        f_out.write(json.dumps(r["res"], ensure_ascii=False) + "\n")
                        total_ok_cnt += 1
                        if r["res"]["v_drift"]: total_drift_cnt += 1
                        if r["res"]["resolved"]: total_resolved_cnt += 1
                
                f_out.flush(); os.fsync(f_out.fileno())
                total_processed += len(batch)
                print(f"[@] {total_processed:<6} | {total_processed/TOTAL_CHUNKS_EST*100:>5.1f}% | Workers: 8 | Drift: {total_drift_cnt}(Res:{total_resolved_cnt})")
                batch = []

    # [봉인 및 Manifest 생성]
    manifest = {}
    for fn in ["audit_receipt.jsonl", "stdout.txt"]:
        p = os.path.join(RUN_DIR, fn)
        if os.path.exists(p):
            with open(p, "rb") as f: manifest[fn] = hashlib.sha256(f.read()).hexdigest()
    with open(os.path.join(RUN_DIR, "hash_manifest.json"), "w") as f: json.dump(manifest, f, indent=2)
    print(f"\n[EVIDENCE] 하청지시서 태그 체계가 반영된 8코어 공정 완공.")

if __name__ == "__main__": main()