import os, sys, json, hashlib, time, threading, shutil, random, re
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# [MANDATE-0] API_KEY 정제 (유니코드 에러 방지)
RAW_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
API_KEY = re.sub(r'[^\x00-\x7F]+', '', RAW_KEY).strip() # ASCII 외 문자 강제 제거

SSOT_ROOT = r"C:\g7core\g7_v1"
INPUT_PATH = r"C:\g6core\g6_v24\data\umr\chunks\fantasy_chunks.jsonl"

# [MANDATE-1] 타임스탬프 기반 운영 폴더
TIMESTAMP = time.strftime("%Y%m%d_%H%M%S")
RUN_DIR = os.path.join(SSOT_ROOT, "runs", f"SEAL_V9_{TIMESTAMP}")
os.makedirs(RUN_DIR, exist_ok=True)

# [가시성-1] 대형 현황판 출력 시스템
class DashboardLogger(object):
    def __init__(self, run_dir):
        self.terminal = sys.stdout
        self.log = open(os.path.join(run_dir, "stdout.txt"), "w", encoding="utf-8")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        self.terminal.flush(); self.log.flush()

sys.stdout = DashboardLogger(RUN_DIR)

# [MANDATE-4] 보초병 배치 (48명)
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
    try:
        v1, v_h1 = get_res(p)
        v_drift, v_resolved, v_final, v_h_final = False, False, v1, v_h1
        votes = [v1]

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
        return {"ok": True, "res": {"row": row_id, "v": v_final, "v_h": v_h_final, "v_drift": v_drift, "resolved": v_resolved}}
    except Exception as e:
        return {"ok": False, "row": row_id, "err": str(e)}

def main():
    print("\n" + "█"*60)
    print(f" ▣ SYSTEM: V9 ULTIMATE DEPLOY BOARD")
    print(f" ▣ RUN_ID: {TIMESTAMP}")
    print(f" ▣ TARGET: {INPUT_PATH}")
    print(f" ▣ STATUS: [48 SENTINELS ACTIVE] [CLEAN_KEY_ENGAGED]")
    print("█"*60 + "\n")

    chunks = []
    with open(INPUT_PATH, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if len(line.strip()) >= 500: chunks.append(line.strip())
            if len(chunks) >= 240: break

    # [가시성-2] 진행 상황 실시간 모니터링
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(tqdm(ex.map(lambda i: seal_worker({"id": i+1, "p": chunks[i]}), range(240)), 
                           total=240, desc=" PROCESSING ", bar_format='{l_bar}{bar:40}{r_bar}{bar:-10b}'))

    res_list = [r["res"] for r in results if r["ok"]]
    err_list = [r for r in results if not r["ok"]]

    # 결과 분석
    rw_a, rw_b = len(res_list[:120]), len(res_list[120:])
    v_drift_cnt = sum(1 for r in res_list if r["v_drift"])
    resolved_cnt = sum(1 for r in res_list if r["resolved"])
    pass_seal = (rw_a >= 90 and rw_b >= 90 and v_drift_cnt == 0 and len(err_list) == 0)

    # 영수증 보존
    with open(os.path.join(RUN_DIR, "audit_receipt.jsonl"), "w", encoding="utf-8") as f:
        for r in res_list: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(RUN_DIR, "verify_report.json"), "w") as f:
        json.dump({"pass": pass_seal, "drift": v_drift_cnt, "resolved": resolved_cnt, "trucks": {"A": rw_a, "B": rw_b}}, f, indent=2)

    # [가시성-3] 최종 리포트 전광판
    print("\n" + "═"*60)
    print(f" 🏁 주행 완료 리포트")
    print(f"  • 합격 여부: {'[ PASS ]' if pass_seal else '[ FAIL ]'}")
    print(f"  • 용접 성공: {resolved_cnt} 건")
    print(f"  • 봉인 실패: {v_drift_cnt} 건")
    print(f"  • 시스템 에러: {len(err_list)} 건")
    print(f"  • 트럭 상황: A({rw_a}/120), B({rw_b}/120)")
    print(f" 📂 영수증: {RUN_DIR}")
    print("═"*60)

    # 쇠사슬 묶기 (Manifest)
    manifest = {}
    for fn in ["verify_report.json", "audit_receipt.jsonl", "stdout.txt"]:
        p = os.path.join(RUN_DIR, fn)
        if os.path.exists(p):
            with open(p, "rb") as f: manifest[fn] = hashlib.sha256(f.read()).hexdigest()
    with open(os.path.join(RUN_DIR, "hash_manifest.json"), "w") as f: json.dump(manifest, f, indent=2)

    sys.exit(0 if pass_seal else 2)

if __name__ == "__main__": main()