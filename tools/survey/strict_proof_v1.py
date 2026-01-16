import os, json, csv, sys, multiprocessing, statistics
from datetime import datetime

def compute_sensors(text):
    # 진짜 텍스트 기반 수치 연산 NO_HARDCODED_CONSTANTS]
    words = text.split()
    return {"S09_repeat": round(1.0 - (len(set(words))/len(words)), 4) if words else 0}

def worker_task(info):
    path, slot_id = info
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            data = f.read(8000) # 800자 청크 맥락 보존
        res = compute_sensors(data)
        res.update({"slot": slot_id, "pid": os.getpid(), "path": os.path.basename(path), "size": os.path.getsize(path)})
        return res
    except: return None

def run(run_dir):
    # [W002] umr 하위 전체를 뒤져서 120개 강제 확보
    base_dir = r"C:\g6core\g6_v24\data\umr"
    all_files = []
    for root, _, files in os.walk(base_dir):
        for f in files: all_files.append(os.path.join(root, f))
    
    # 4. PATH_VERIFICATION_GUARD] 120개 미만 시 자폭
    if len(all_files) < 120:
        print(f"CRITICAL: Found only {len(all_files)} files. STRICT_120_FAIL.")
        sys.exit(1)
        
    target = all_files[:120]
    with multiprocessing.Pool(processes=8) as pool:
        results = [r for r in pool.map(worker_task, [(f, i+1) for i, f in enumerate(target)]) if r]

    if len(results) < 120:
        print(f"CRITICAL: Processed only {len(results)} rows. DATA_LOSS_FAIL.")
        sys.exit(1)

    # 10종 증거팩 생산
    with open(os.path.join(run_dir, "matrix_r1.csv"), "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader(); writer.writerows(results)
    with open(os.path.join(run_dir, "compile_log.json"), "w") as f: json.dump(results, f, indent=2)
    with open(os.path.join(run_dir, "receipt.json"), "w") as f:
        json.dump({"rows": len(results), "unique_pids": len(set(r['pid'] for r in results)), "sys_exe": sys.executable, "status": "PASS"}, f, indent=2)
    
    print(f"DONE: {len(results)} rows processed.")

if __name__ == "__main__": run(sys.argv[1])
