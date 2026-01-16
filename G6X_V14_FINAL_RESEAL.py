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
RUN_DIR = os.path.join(SSOT_ROOT, "runs", f"FINAL_RESEAL_{TIMESTAMP}")
os.makedirs(RUN_DIR, exist_ok=True)

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
    def close(self):
        if not self.log.closed: self.log.close()

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
    prompt = "JSON only. {\"verdict\":\"ALLOW|BLOCK\",\"why\":\"short\"}\nPayload: " + p
    for _ in range(3):
        try:
            r = client.models.generate_content(model=MODEL_ID, contents=prompt, config=config)
            j = json.loads(r.text)
            combined = f"{j.get('verdict', 'BLOCK')}|{j.get('why', '')}"
            return combined, hashlib.sha256(combined.encode()).hexdigest(), True
        except: time.sleep(1)
    return "BLOCK|error", hashlib.sha256("BLOCK|error".encode()).hexdigest(), False

def seal_worker(task):
    row_id, p, sentinels = task['id'], task['p'], task['sentinels']
    c1, h1, ok1 = get_res(p)
    v_drift, v_resolved, v_final_combined, v_h_final = False, False, c1, h1
    
    cycle_id = (row_id - 1) % 240 + 1
    if cycle_id in sentinels and ok1:
        c2, h2, ok2 = get_res(p)
        if ok2 and h1 != h2:
            v_drift = True
            votes = [c1, c2]
            for _ in range(3):
                cn, _, okn = get_res(p)
                if okn: votes.append(cn)
            v_counts = {v: votes.count(v) for v in set(votes)}
            v_final_combined = max(v_counts, key=v_counts.get)
            if v_counts[v_final_combined] >= 4:
                v_resolved = True # 형님 지시사항: Resolved 플래그 명시
                v_h_final = hashlib.sha256(v_final_combined.encode()).hexdigest()
    
    parts = v_final_combined.split('|')
    return {"ok": ok1, "res": {"row": row_id, "v": parts[0], "why": parts[1] if len(parts)>1 else "", 
                               "v_h": v_h_final, "v_drift": v_drift, "resolved": v_resolved}}

def main():
    print(f"### [G6X ULTIMATE_RESEAL] 12GB 본 공정 점화")
    total_processed, total_ok_cnt, total_error_cnt, total_drift_cnt, total_resolved_cnt = 0, 0, 0, 0, 0
    receipt_path = os.path.join(RUN_DIR, "audit_receipt.jsonl")
    
    with open(INPUT_PATH, "r", encoding="utf-8", errors="replace") as f_in, \
         open(receipt_path, "a", encoding="utf-8") as f_out:
        
        batch = []
        for i, line in enumerate(f_in):
            batch.append({"id": i + 1, "p": line.strip()})
            if len(batch) >= 240:
                now = datetime.now()
                current_workers = 6 if not (now.hour > 5 or (now.hour == 5 and now.minute >= 30)) else 4
                
                dynamic_random = random.sample([n for n in range(1, 241) if n not in FIXED_SENTINELS], 12)
                current_sentinels = set(FIXED_SENTINELS + dynamic_random)
                for t in batch: t['sentinels'] = current_sentinels
                
                with ThreadPoolExecutor(max_workers=current_workers) as ex:
                    results = list(ex.map(seal_worker, batch))
                
                batch_ok = 0
                for r in results:
                    if r["ok"]:
                        f_out.write(json.dumps(r["res"], ensure_ascii=False) + "\n")
                        total_ok_cnt += 1; batch_ok += 1
                        if r["res"]["v_drift"]: total_drift_cnt += 1
                        if r["res"]["resolved"]: total_resolved_cnt += 1
                    else: total_error_cnt += 1
                
                f_out.flush(); os.fsync(f_out.fileno())
                total_processed += len(batch)
                print(f"[@] {total_processed:<6} | {total_processed/TOTAL_CHUNKS_EST*100:>5.1f}% | Workers: {current_workers} | Drift: {total_drift_cnt}(Res:{total_resolved_cnt})")
                batch = []

    # [FINAL SEALING & MANIFEST]
    unresolved = total_drift_cnt - total_resolved_cnt
    is_pass = (total_error_cnt == 0 and unresolved == 0) # 형님 추천 판정 기준
    
    with open(os.path.join(RUN_DIR, "verify_report.json"), "w") as f:
        json.dump({"pass": is_pass, "total": total_processed, "drift": total_drift_cnt, "resolved": total_resolved_cnt, "unresolved": unresolved}, f, indent=2)
    
    with open(os.path.join(RUN_DIR, "exitcode.txt"), "w") as f: f.write("0" if is_pass else "2")
    
    logger.flush(); logger.close()
    sys.stdout = logger.terminal
    
    # Manifest 생성 (형님 지시: 외부 감사 대비)
    manifest = {}
    for fn in ["audit_receipt.jsonl", "stdout.txt", "exitcode.txt", "verify_report.json"]:
        p = os.path.join(RUN_DIR, fn)
        if os.path.exists(p):
            with open(p, "rb") as f: manifest[fn] = hashlib.sha256(f.read()).hexdigest()
    with open(os.path.join(RUN_DIR, "hash_manifest.json"), "w") as f: json.dump(manifest, f, indent=2)
    
    print(f"\n[EVIDENCE_MANDATED_AUDIT] 봉인 완료. Manifest 생성됨: {RUN_DIR}")
    input("Audit Done. Press Enter...")

if __name__ == "__main__": main()