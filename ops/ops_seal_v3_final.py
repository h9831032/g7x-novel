import os, sys, json, csv, time, hashlib, threading, io, glob
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# [MANDATE-0] FAIL_FAST & 환경 방어 [cite: 5, 21, 2026-01-04]
API_KEY = os.getenv("GEMINI_API_KEY")
SSOT_ROOT = r"C:\g7core\g7_v1"
if not API_KEY: sys.exit(2) # 하드코딩 키 금지 [cite: 5, 2026-01-04]

RUN_ID = f"SEAL_V3_{int(time.time())}"
RUN_DIR = os.path.join(SSOT_ROOT, "runs", RUN_ID)
os.makedirs(RUN_DIR, exist_ok=True)

# [MANDATE-5] stdout/stderr 파일 캡처 강제 [cite: 5, 2026-01-04]
log_f = open(os.path.join(RUN_DIR, "stdout.txt"), "w", encoding="utf-8")
err_f = open(os.path.join(RUN_DIR, "stderr.txt"), "w", encoding="utf-8")
sys.stdout = log_f
sys.stderr = err_f

# [MANDATE-1, 2, 3, 6] 정책 및 헌법 정의 [cite: 5, 2026-01-04]
TRUCK_SIZE = 120
RW_LIMIT = 90
SENTINELS = [1, 7, 13, 21, 34, 55, 60, 61, 73, 89, 97, 101, 109, 113, 120, 3, 17, 44, 77, 99]
SCHEMA_STR = '{"verdict":"ALLOW|WARN|BLOCK","why":"short","foreshadowing":bool,"contradictions":[]}'
POLICY = {
    "truck": TRUCK_SIZE, "slots": {"A": 60, "B": 36, "C": 18, "D": 6},
    "sentinels": SENTINELS, "model": "gemini-2.5-flash", "temp": 0, "schema": SCHEMA_STR
}
POLICY_HASH = hashlib.sha256(json.dumps(POLICY, sort_keys=True).encode()).hexdigest()

DRIFT_TOTAL = 0
SAVE_LOCK = threading.Lock()
GEMINI_SEM = threading.Semaphore(4) # 4 Concurrent Calls [cite: 5, 2026-01-04]

def get_canonical_hash(res):
    """[MANDATE-2, 3] 고정 스키마 기반 캐노니컬 해시 [cite: 5, 16, 2026-01-04]"""
    try:
        core = {
            "v": str(res.get("verdict", "BLOCK")).upper(),
            "w": str(res.get("why", ""))[:80],
            "f": bool(res.get("foreshadowing", False)),
            "c": len(res.get("contradictions", []))
        }
        return hashlib.sha256(json.dumps(core, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    except: return "JSON_PARSE_FAIL"

def audit_worker(task, tid):
    global DRIFT_TOTAL
    client = genai.Client(api_key=API_KEY)
    config = types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
    prompt = f"Return JSON only. Schema: {SCHEMA_STR}\nPayload: {task['p']}"

    try:
        with GEMINI_SEM:
            r1 = client.models.generate_content(model=POLICY["model"], contents=prompt, config=config)
            res1 = json.loads(r1.text)
            h1 = get_canonical_hash(res1)
            
            is_drift = False
            slot = ((task['id'] - 1) % TRUCK_SIZE) + 1
            if slot in SENTINELS: # [MANDATE-2] 센티넬 고정 재질의 [cite: 5, 2026-01-04]
                r2 = client.models.generate_content(model=POLICY["model"], contents=prompt, config=config)
                h2 = get_canonical_hash(json.loads(r2.text))
                if h1 != h2:
                    with SAVE_LOCK: DRIFT_TOTAL += 1
                    is_drift = True

        # [MANDATE-5] audit_receipt.jsonl (row 단위 영수증) [cite: 11, 22, 2026-01-04]
        receipt = {"p_hash": POLICY_HASH, "row": task['id'], "h": h1, "v": res1.get("verdict"), "d": is_drift}
        with SAVE_LOCK:
            with open(os.path.join(RUN_DIR, "audit_receipt.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps(receipt, ensure_ascii=False) + "\n")
            with open(os.path.join(RUN_DIR, "result_packet.tsv"), "a", newline="", encoding="utf-8") as f:
                csv.writer(f, delimiter="\t").writerow([task['id'], True, res1.get("verdict"), h1, is_drift])
        return {"ok": True, "v": res1.get("verdict"), "drift": is_drift}
    except:
        return {"ok": False, "v": "ERROR", "drift": False}

def main():
    # [MANDATE-4] 12GB 대응 스트리밍 적재 (2500자 청크 240개) [cite: 5, 2026-01-04]
    input_files = glob.glob(os.path.join(r"C:\g6core\g6_v24\data\umr\chunks", "*"))
    input_file = max(input_files, key=os.path.getsize)
    chunks = []
    with open(input_file, "r", encoding="utf-8", errors="replace") as f:
        while len(chunks) < 240:
            chunk = f.read(2500)
            if not chunk: break
            if len(chunk) >= 500: chunks.append(chunk)
    
    if len(chunks) < 240: # [MANDATE-0] 240 미만 FAIL [cite: 5, 2026-01-04]
        print("[FAIL_FAST] Under 240 chunks."); sys.exit(2)

    # [MANDATE-5] work_packet.tsv 생성 [cite: 5, 2026-01-04]
    with open(os.path.join(RUN_DIR, "work_packet.tsv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["row_id", "truck", "p_hash", "sentinel"])
        for i in range(240):
            tid = "A" if i < 120 else "B"
            is_s = (i % 120 + 1) in SENTINELS
            writer.writerow([i+1, tid, hashlib.sha256(chunks[i].encode()).hexdigest(), is_s])

    with ThreadPoolExecutor(max_workers=8) as ex:
        res_a = list(tqdm(ex.map(lambda i: audit_worker({"id": i+1, "p": chunks[i]}, "A"), range(120)), total=120, desc="TRUCK-A"))
        res_b = list(tqdm(ex.map(lambda i: audit_worker({"id": i+121, "p": chunks[i+120]}, "B"), range(120)), total=120, desc="TRUCK-B"))

    # [MANDATE-1] 트럭별 독립 판정 [cite: 5, 2026-01-04]
    rw_a = sum(1 for r in res_a if r['ok'] and r['v'] in ["ALLOW", "WARN"])
    rw_b = sum(1 for r in res_b if r['ok'] and r['v'] in ["ALLOW", "WARN"])
    pass_op = (rw_a >= RW_LIMIT and rw_b >= RW_LIMIT)
    pass_seal = (pass_op and DRIFT_TOTAL == 0) # [MANDATE-2] drift=FAIL [cite: 5, 21, 2026-01-04]

    # [MANDATE-5, 6] verify_report.json (최종 도장) [cite: 11, 22, 2026-01-04]
    report = {
        "pass_op": pass_op, "pass_seal": pass_seal, "drift_total": DRIFT_TOTAL,
        "truck_rw": {"A": rw_a, "B": rw_b}, "policy_hash": POLICY_HASH, "exitcode": 0 if pass_seal else 2
    }
    with open(os.path.join(RUN_DIR, "verify_report.json"), "w") as f: json.dump(report, f, indent=2)
    with open(os.path.join(RUN_DIR, "exitcode.txt"), "w") as f: f.write(str(report['exitcode']))

    # [MANDATE-5] hash_manifest.json [cite: 11, 22, 2026-01-04]
    manifest = {f: hashlib.sha256(open(os.path.join(RUN_DIR, f), "rb").read()).hexdigest() 
                for f in ["stdout.txt", "work_packet.tsv", "result_packet.tsv", "verify_report.json", "audit_receipt.jsonl"]}
    with open(os.path.join(RUN_DIR, "hash_manifest.json"), "w") as f: json.dump(manifest, f, indent=2)

    log_f.close(); err_f.close()
    sys.exit(report['exitcode'])

if __name__ == "__main__": main()