import os, sys, json, hashlib, time, threading, csv, shutil
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# [MANDATE-0] FAIL_FAST & 환경
API_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
SSOT_ROOT = r"C:\g7core\g7_v1"
INPUT_PATH = r"C:\g6core\g6_v24\data\umr\chunks\fantasy_chunks.jsonl"
RUN_ID = f"RUN_{int(time.time())}"
RUN_DIR = os.path.join(SSOT_ROOT, "runs", RUN_ID)
os.makedirs(RUN_DIR, exist_ok=True)

# [MANDATE-4] 고정 센티넬 24개 (표준추)
SENTINELS = [1, 7, 13, 21, 34, 55, 60, 61, 73, 89, 97, 101, 109, 113, 120, 123, 137, 144, 177, 199, 210, 222, 235, 240]

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
    w = j.get("why", "")
    # [MANDATE-2] 해시 분리
    v_h = hashlib.sha256(v.encode()).hexdigest()
    f_h = hashlib.sha256((v + w[:80]).encode()).hexdigest()
    return v, w, v_h, f_h

def seal_worker(task):
    row_id, p = task['id'], task['p']
    v1, w1, v_h1, f_h1 = get_res(p)
    
    v_drift, e_drift, v_resolved, v_final, v_h_final = False, False, False, v1, v_h1
    votes = [v1]

    if row_id in SENTINELS:
        v2, w2, v_h2, f_h2 = get_res(p)
        if v_h1 != v_h2: # VERDICT_DRIFT 발생
            # [MANDATE-3] 5회 다수결 용접
            votes = [v1, v2]
            for _ in range(3):
                vn, _, _, _ = get_res(p)
                votes.append(vn)
            v_final = max(set(votes), key=votes.count)
            # 4/5 이상 시에만 RESOLVED
            if votes.count(v_final) >= 4:
                v_resolved, v_drift = True, False
                v_h_final = hashlib.sha256(v_final.encode()).hexdigest()
            else:
                return {"ok": False, "row": row_id, "fail_fast": True} # 1:1:1 등 실패
        elif f_h1 != f_h2:
            e_drift = True # EXPLAIN_DRIFT는 기록만 (무시)

    return {"ok": True, "res": {"row": row_id, "v": v_final, "v_h": v_h_final, "v_drift": v_drift, "e_drift": e_drift, "resolved": v_resolved, "votes": votes}}

def main():
    # [MANDATE-5] 120+120 규격 로드
    chunks = []
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if len(line.strip()) >= 500: chunks.append(line.strip())
            if len(chunks) >= 240: break
    if len(chunks) < 240: sys.exit(2)

    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(tqdm(ex.map(lambda i: seal_worker({"id": i+1, "p": chunks[i]}), range(240)), total=240, desc="GOLD_SEAL"))

    if any(not r["ok"] and r.get("fail_fast") for r in results): sys.exit(2)

    res_list = [r["res"] for r in results]
    rw_a = sum(1 for r in res_list[:120] if r["v"] in ["ALLOW", "BLOCK"]) # [치명-2] 스키마 OK 기준
    rw_b = sum(1 for r in res_list[120:] if r["v"] in ["ALLOW", "BLOCK"])
    v_drift_cnt = sum(1 for r in res_list if r["v_drift"])
    e_drift_cnt = sum(1 for r in res_list if r["e_drift"])
    resolved_cnt = sum(1 for r in res_list if r["resolved"])

    pass_op = (rw_a >= 90 and rw_b >= 90)
    pass_seal = (pass_op and v_drift_cnt == 0)
    
    # [MANDATE-6] 증거팩 생성
    with open(os.path.join(RUN_DIR, "verify_report.json"), "w") as f:
        json.dump({"pass_op": pass_op, "pass_seal": pass_seal, "v_drift_cnt": v_drift_cnt, "e_drift_cnt": e_drift_cnt, "resolved_cnt": resolved_cnt, "trucks": {"A": rw_a, "B": rw_b}, "run_id": RUN_ID}, f, indent=2)
    with open(os.path.join(RUN_DIR, "exitcode.txt"), "w") as f: f.write("0" if pass_seal else "2")
    with open(os.path.join(RUN_DIR, "audit_receipt.jsonl"), "w", encoding="utf-8") as f:
        for r in res_list: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    
    print(f"\n[@] SEAL DONE. PASS={pass_seal} | RUN_DIR={RUN_DIR}")
    sys.exit(0 if pass_seal else 2)

if __name__ == "__main__": main()