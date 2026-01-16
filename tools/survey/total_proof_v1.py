import os, json, csv, sys, multiprocessing, glob, hashlib
from datetime import datetime

def compute_sensors(text):
    words = text.split()
    return {"S09": round(1.0 - (len(set(words))/len(words)), 4) if words else 0}

def worker_task(info):
    path, slot_id = info
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read(5000)
    res = compute_sensors(data)
    res.update({"slot": slot_id, "pid": os.getpid(), "path": os.path.basename(path)})
    return res

def run(run_dir):
    input_dir = r"C:\g6core\g6_v24\data\umr\chunks"
    all_files = []
    for root, _, files in os.walk(input_dir):
        for f in files: all_files.append(os.path.join(root, f))
    
    target = all_files[:120]
    with multiprocessing.Pool(processes=8) as pool:
        results = pool.map(worker_task, [(f, i+1) for i, f in enumerate(target)])
    
    # 1. matrix_r1.csv 생성
    csv_path = os.path.join(run_dir, "matrix_r1.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader(); writer.writerows(results)
    
    # 2. receipt.json & compile_log.json
    with open(os.path.join(run_dir, "compile_log.json"), "w") as f: json.dump(results, f, indent=2)
    with open(os.path.join(run_dir, "receipt.json"), "w") as f:
        json.dump({"input_dir": input_dir, "rows": len(results), "unique_pids": len(set(r['pid'] for r in results)), "sys_exe": sys.executable}, f, indent=2)
    
    # 3. file_list.txt & hash_manifest
    files = os.listdir(run_dir)
    with open(os.path.join(run_dir, "file_list.txt"), "w") as f: f.write("\n".join(files))
    
    print(f"DONE: {len(results)} rows.")

if __name__ == "__main__": run(sys.argv[1])
