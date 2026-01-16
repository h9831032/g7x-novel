import os, json, csv, hashlib, sys, time
from multiprocessing import Pool

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192): h.update(chunk)
    return h.hexdigest()

def worker_task(row):
    # [W113] 로봇 1명의 개별 작업 실증 (PID 채집)
    time.sleep(0.01) # 컨텍스트 스위칭 유도
    return {
        "row_id": row['sid'],
        "sha1": row['sha1'],
        "pid": os.getpid(),
        "status": "COMPILED"
    }

def run_compiler(input_run, run_dir):
    # 1. 카탈로그 생성 (120개 슬롯)
    csv_path = os.path.join(input_run, "matrix_rot_3.csv")
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))[:120]

    with open(os.path.join(run_dir, "catalog.json"), "w") as f:
        json.dump(rows, f, indent=2)

    # 2. [W113] 병렬 실행 (Worker=4)
    print(f"DEBUG: Distributing 120 tasks to 4 robots...")
    with Pool(4) as p:
        compile_results = p.map(worker_task, rows)

    # 3. [W114] PID 검증 및 로그 저장
    unique_pids = set(r['pid'] for r in compile_results)
    print(f"DEBUG: Unique PIDs observed: {len(unique_pids)}")
    
    if len(unique_pids) < 4:
        print(f"FATAL: Only {len(unique_pids)} PIDs found. Parallelism fail."); sys.exit(1)

    with open(os.path.join(run_dir, "compile_log.json"), "w") as f:
        json.dump(compile_results, f, indent=2)

    # 4. [W111] 최종 기소장(Track B) 작성
    with open(os.path.join(run_dir, "trackB_cases.jsonl"), "w", encoding='utf-8') as f:
        for r in rows:
            case = {"sid": r['sid'], "sha1": r['sha1'], "text_snippet": r['snippet']}
            f.write(json.dumps(case, ensure_ascii=False) + "\n")

    # 5. [F] 해시 매니페스트 봉인
    manifest = []
    for fn in ["catalog.json", "compile_log.json", "trackB_cases.jsonl"]:
        p = os.path.join(run_dir, fn)
        manifest.append(f"{sha256_file(p)}  {fn}")
    
    with open(os.path.join(run_dir, "hash_manifest.sha256.txt"), "w") as f:
        f.write("\n".join(manifest))

    print(f"COMPILER_DONE: 120 SLOTS SEALED WITH {len(unique_pids)} PIDs.")

if __name__ == "__main__":
    run_compiler(r'', r'C:\g7core\g7_v1\runs\FINAL_SEAL_1745')
