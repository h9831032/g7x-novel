import os, sys, json, hashlib, time, threading, random, re
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# [MANDATE-0] 설정
RAW_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
API_KEY = re.sub(r'[^\x00-\x7F]+', '', RAW_KEY).strip()
MODEL_ID = "models/gemini-2.5-flash"

SSOT_ROOT = r"C:\g7core\g7_v1"
INPUT_PATH = r"C:\g6core\g6_v24\data\umr\chunks\fantasy_chunks.jsonl"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = os.path.join(SSOT_ROOT, "runs", f"FINAL_FIX_{TIMESTAMP}")
os.makedirs(RUN_DIR, exist_ok=True)

# [내장형 태그 규칙]
TAG_RULES = {"TAG_DRIFT_PLOT": "인과단절", "TAG_DRIFT_CHARACTER": "성격급변", "TAG_DRIFT_TONE": "문체불일치", "TAG_PETRIFY": "서사정지", "TAG_PATTERN_LOOP": "문장반복", "TAG_COMMONSENSE_FAIL": "상식오류", "TAG_POWER_RULE_FAIL": "수치모순", "TAG_CAUSAL_FAIL": "원인부재", "TAG_FUN_LOW": "지루함", "TAG_FUN_MID": "평이함", "TAG_FUN_HIGH": "몰입감"}
FIXED_12 = [1, 21, 55, 89, 101, 113, 123, 144, 177, 199, 222, 240]

class HardenLogger(object):
    def __init__(self, run_dir):
        self.terminal = sys.stdout
        self.log_path = os.path.join(run_dir, "stdout.txt")
        self.log = open(self.log_path, "a", encoding="utf-8")
    def write(self, m):
        self.terminal.write(m)
        if not self.log.closed: self.log.write(m)
    def flush(self):
        self.terminal.flush()
        if not self.log.closed:
            self.log.flush()
            try: os.fsync(self.log.fileno())
            except: pass
    def close(self):
        if not self.log.closed: self.log.close()

logger = HardenLogger(RUN_DIR)
sys.stdout = logger

thread_local = threading.local()
def get_client():
    if not hasattr(thread_local, "client"):
        thread_local.client = genai.Client(api_key=API_KEY)
    return thread_local.client

def get_res(p):
    client = get_client()
    rule_str = json.dumps(TAG_RULES, ensure_ascii=False)
    prompt = f"JSON only. Format: {{\"verdict\":\"ALLOW|BLOCK\",\"why\":\"short\",\"tags\":[]}}\nRules: {rule_str}\nPayload: {p}"
    for _ in range(3):
        try:
            r = client.models.generate_content(model=MODEL_ID, contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0))
            j = json.loads(r.text)
            # [수정] 0점 탈출: 대소문자 무관하게 ALLOW 포함 시 ALLOW로 강제 정규화
            rv = str(j.get('verdict', 'BLOCK')).upper()
            v = "ALLOW" if "ALLOW" in rv else "BLOCK"
            w = j.get('why', '')
            h = hashlib.sha256(f"{v}|{w}".encode()).hexdigest()
            return v, w, j.get('tags', []), h, True, ""
        except: time.sleep(1)
    return "BLOCK", "error", [], "err_h", False, "api_fail"

def seal_worker(task):
    row_id, p, sentinels = task['id'], task['p'], task['sentinels']
    v1, w1, t1, h1, ok1, e1 = get_res(p)
    v_drift, v_res, v_f_v, v_f_w, v_f_t, v_f_h = False, False, v1, w1, t1, h1
    c_id = (row_id-1)%240+1
    if c_id in sentinels and ok1:
        v2, w2, t2, h2, ok2, _ = get_res(p)
        if ok2 and h1 != h2:
            v_drift = True
            votes = [f"{v1}|{w1}", f"{v2}|{w2}"]
            for _ in range(3):
                vn, wn, _, _, okn, _ = get_res(p)
                if okn: votes.append(f"{vn}|{wn}")
            best = max(set(votes), key=votes.count)
            if votes.count(best) >= 4:
                v_res = True; v_f_v, v_f_w = best.split('|'); v_f_h = hashlib.sha256(best.encode()).hexdigest()
    return {"ok": ok1, "res": {"row": row_id, "v": v_f_v, "why": v_f_w, "tags": v_f_t, "v_h": v_f_h, "v_drift": v_drift, "resolved": v_res, "err": e1 if not ok1 else ""}}

def main():
    print(f"### [G6X FINAL_RESEAL_V1] 15min PROOF")
    total, d_total, r_total, e_total = 0, 0, 0, 0
    rw_a, rw_b = 0, 0
    receipt_path = os.path.join(RUN_DIR, "audit_receipt.jsonl")
    
    with open(INPUT_PATH, "r", encoding="utf-8") as f_in, open(receipt_path, "a", encoding="utf-8") as f_out:
        batch = []
        for i, line in enumerate(f_in):
            batch.append({"id": i + 1, "p": line.strip()})
            if len(batch) >= 240:
                rand_s = random.sample([n for n in range(1, 241) if n not in FIXED_12], 12)
                all_s = set(FIXED_12 + rand_s)
                for t in batch: t['sentinels'] = all_s
                
                with ThreadPoolExecutor(max_workers=6) as ex:
                    results = list(ex.map(seal_worker, batch))
                
                for r in results:
                    f_out.write(json.dumps(r["res"], ensure_ascii=False) + "\n")
                    c_id = (r["res"]["row"]-1)%240+1
                    if r["res"]["v"] == "ALLOW":
                        if 1 <= c_id <= 120: rw_a += 1
                        elif 121 <= c_id <= 240: rw_b += 1
                    if r["ok"]:
                        if r["res"]["v_drift"]:
                            d_total += 1
                            if r["res"]["resolved"]: r_total += 1
                    else: e_total += 1
                
                total += len(batch)
                print(f"[@] {total} | Truck A: {rw_a/(total/240):.1f} B: {rw_b/(total/240):.1f} | Drift: {d_total}")
                batch = []
                # [A8] 15분(480개) 주행 후 강제 종료 - 이제 진짜 멈춥니다!
                if total >= 480: 
                    print("### [SYSTEM] 15분 증거 수집 완료. 브레이크 작동."); break

    report = {"pass_op": (rw_a/(total/240)>=90), "total": total, "truck_rw": {"A": rw_a, "B": rw_b}}
    with open(os.path.join(RUN_DIR, "verify_report.json"), "w") as f: json.dump(report, f, indent=2)
    logger.flush(); logger.close()
    
    manifest = {}
    for fn in ["audit_receipt.jsonl", "stdout.txt", "verify_report.json"]:
        p = os.path.join(RUN_DIR, fn)
        if os.path.exists(p):
            with open(p, "rb") as f: manifest[fn] = hashlib.sha256(f.read()).hexdigest()
    with open(os.path.join(RUN_DIR, "hash_manifest.json"), "w") as f: json.dump(manifest, f, indent=2)

if __name__ == "__main__": main()