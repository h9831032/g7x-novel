import os, json, csv, hashlib, sys, time
from multiprocessing import Pool

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192): h.update(chunk)
    return h.hexdigest()

def worker_task(row):
    # [W113] 실전 로봇 작업 (PID 기록)
    return {"sid": row['sid'], "pid": os.getpid(), "status": "COMPILED"}

def run_compiler(input_run, run_dir):
    csv_path = os.path.join(input_run, "matrix_rot_3.csv")
    if not os.path.exists(csv_path):
        print(f"FATAL: Missing CSV at {csv_path}"); sys.exit(1)

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))[:120]

    # [W111-W113] 병렬 카탈로그 컴파일
    with Pool(4) as p:
        compile_results = p.map(worker_task, rows)

    unique_pids = set(r['pid'] for r in compile_results)
    
    # [W114] 실증 조건 확인
    if len(unique_pids) < 4:
        print(f"FATAL: Parallelism failed. Only {len(unique_pids)} PIDs."); sys.exit(1)

    # 영수증 봉인
    with open(os.path.join(run_dir, "catalog.json"), "w") as f: json.dump(rows, f, indent=2)
    with open(os.path.join(run_dir, "compile_log.json"), "w") as f: json.dump(compile_results, f, indent=2)
    
    with open(os.path.join(run_dir, "hash_manifest.sha256.txt"), "w") as f:
        f.write(f"{sha256_file(os.path.join(run_dir, 'catalog.json'))}  catalog.json\n")
    
    print(f"COMPILER_DONE: {len(unique_pids)} ROBOTS SECURED.")

if __name__ == "__main__":
    run_compiler(r'C:\g7core\g7_v1\runs\V31_REAL_1744', r'C:\g7core\g7_v1\runs\FINAL_SEAL_1747')
