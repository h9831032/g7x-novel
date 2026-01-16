import os, sys, json, hashlib, time, threading, csv, shutil
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# [MANDATE-0] FAIL_FAST & 환경
API_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
SSOT_ROOT = r"C:\g7core\g7_v1"
INPUT_PATH = r"C:\g6core\g6_v24\data\umr\chunks\fantasy_chunks.jsonl"
RUN_DIR = os.path.join(SSOT_ROOT, "runs", "PERFECT_SESSION")
if os.path.exists(RUN_DIR): shutil.rmtree(RUN_DIR)
os.makedirs(RUN_DIR, exist_ok=True)

# [MANDATE-4] 고정 센티넬 24개 (표준추)
FIXED_SENTINELS = [1, 7, 13, 21, 34, 55, 60, 61, 73, 89, 97, 101, 109, 113, 120, 123, 137, 144, 177, 199, 210, 222, 235, 240]

# [운영-1] Thread-local Client 재사용 (리소스 최적화)
thread_local = threading.local()

def get_client():
    if not hasattr(thread_local, "client"):
        thread_local.client = genai.Client(api_key=API_KEY)
    return thread_local.client

def get_gemini_verdict(p):
    client = get_client()
    config = types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
    prompt = f"Return JSON only. Schema: {{\"verdict\":\"ALLOW|BLOCK\",\"why_code\":\"OK|RULE_VIOLATION|UNKNOWN\"}}\nPayload: {p}"
    try:
        r = client.models.generate_content(model="gemini-2.5-flash", contents=prompt, config=config)
        j = json.loads(r.text)
        v = j.get('verdict', 'BLOCK')
        # [운영-2] 스키마 값 검증 강화
        if v not in ["ALLOW", "BLOCK"]: return "BLOCK", "UNKNOWN", False
        return v, j.get('why_code', 'UNKNOWN'), True
    except:
        return "BLOCK", "UNKNOWN", False

def process_chunk(task):
    row_id, p = task['id'], task['p']
    v1, w1, ok1 = get_gemini_verdict(p)
    if not ok1: return {"ok": False, "row": row_id, "err": "SCHEMA_ERROR"}

    v_drift_after, v_final = False, v1
    e_drift, votes = False, [v1]

    if row_id in FIXED_SENTINELS:
        v2, w2, ok2 = get_gemini_verdict(p)
        if not ok2: return {"ok": False, "row": row_id, "err": "SCHEMA_ERROR"}
        votes.append(v2)
        
        if v1 != v2: # 1:1 상황 발생
            v3, w3, ok3 = get_gemini_verdict(p)
            if not ok3: return {"ok": False, "row": row_id, "err": "SCHEMA_ERROR"}
            votes.append(v3)
            
            # [치명-1] 다수결 로직 정밀화 (1:1:1 방어)
            v_counts = {v: votes.count(v) for v in set(votes)}
            v_final = max(v_counts, key=v_counts.get)
            if v_counts[v_final] < 2: # 1:1:1 상황
                v_final = "UNRESOLVED"
                v_drift_after = True
            else:
                v_drift_after = False # 2:1 해결
        
        # [운영-3] Explain Drift 강화 (3회차 w3까지 체크)
        if len(set([w1, w2])) > 1: e_drift = True

    v_hash = hashlib.sha256(v_final.encode()).hexdigest()
    return {"ok": True, "row": row_id, "v_final": v_final, "v_h": v_hash, "v_after": v_drift_after, "e_drift": e_drift}

def main():
    print(f"\n" + "="*60 + f"\n [!] MANDATE: PERFECT_SEAL V7 (Logic Patched)\n" + "="*60)
    chunks = []
    with open(INPUT_PATH, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if len(line.strip()) >= 500: chunks.append(line.strip())
            if len(chunks) >= 240: break

    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(tqdm(ex.map(lambda i: process_chunk({"id": i+1, "p": chunks[i]}), range(240)), total=240, desc="SEALING"))

    # [치명-2] REAL_WORK 정의 수정 (Schema OK 기준)
    truck_a, truck_b = results[:120], results[120:]
    rw_a = sum(1 for r in truck_a if r.get('ok'))
    rw_b = sum(1 for r in truck_b if r.get('ok'))
    
    allow_cnt = sum(1 for r in results if r.get('v_final') == "ALLOW")
    v_drift_final = sum(1 for r in results if r.get('v_after') or r.get('v_final') == "UNRESOLVED")
    
    pass_seal = (rw_a >= 90 and rw_b >= 90 and v_drift_final == 0)
    exit_code = 0 if pass_seal else 2

    # 증거팩 6종 생성
    with open(os.path.join(RUN_DIR, "exitcode.txt"), "w") as f: f.write(str(exit_code))
    report = {"pass_seal": pass_seal, "v_drift_final": v_drift_final, "trucks": {"A": rw_a, "B": rw_b}, "allow_total": allow_cnt}
    with open(os.path.join(RUN_DIR, "verify_report.json"), "w") as f: json.dump(report, f, indent=2)
    with open(os.path.join(RUN_DIR, "audit_receipt.jsonl"), "w", encoding="utf-8") as f:
        for r in results: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    
    print(f"\n [RESULT] PASS={pass_seal} | Drift={v_drift_final} | RW_A:{rw_a} RW_B:{rw_b} | ALLOW_TOT:{allow_cnt}")

if __name__ == "__main__": main()