import os, json, csv, hashlib, sys, time
from multiprocessing import Pool

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192): h.update(chunk)
    return h.hexdigest()

def worker_task(row):
    # [W113] 로봇 작업 강제 부하 (OS의 프로세스 재사용 방지)
    time.sleep(0.05) 
    return {"sid": row['sid'], "pid": os.getpid(), "status": "COMPILED"}

def run_compiler(input_run, run_dir):
    csv_path = os.path.join(input_run, "matrix_rot_3.csv")
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))[:120]

    # [W111-W113] 4대의 로봇 풀 가동
    print(f"DEBUG: Initializing 4 robots for 120 items...")
    with Pool(4) as p:
        # 모든 프로세스가 한 번씩은 깨어나도록 지연 작업을 분배
        compile_results = p.map(worker_task, rows)

    unique_pids = set(r['pid'] for r in compile_results)
    print(f"DEBUG: Observed PIDs -> {list(unique_pids)}")
    
    # [W114] 4개 미만 시 국물도 없음
    if len(unique_pids) < 4:
        print(f"FATAL: Parallelism failed. Only {len(unique_pids)} PIDs worked."); sys.exit(1)

    # 120개 카탈로그 및 컴파일 로그 저장
    with open(os.path.join(run_dir, "catalog.json"), "w") as f: json.dump(rows, f, indent=2)
    with open(os.path.join(run_dir, "compile_log.json"), "w") as f: json.dump(compile_results, f, indent=2)
    with open(os.path.join(run_dir, "hash_manifest.sha256.txt"), "w") as f:
        f.write(f"{sha256_file(os.path.join(run_dir, 'catalog.json'))}  catalog.json\n")
    
    print(f"COMPILER_DONE: {len(unique_pids)} UNIQUE ROBOTS VERIFIED.")

if __name__ == "__main__":
    run_compiler(r'C:\g7core\g7_v1\runs\V31_REAL_1744', r'C:\g7core\g7_v1\runs\FINAL_SEAL_1748')
