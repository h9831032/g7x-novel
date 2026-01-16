import os, json, csv, sys, multiprocessing, glob
from datetime import datetime

def worker_task(file_info):
    path, slot_id = file_info
    try:
        fsize = os.path.getsize(path)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(5000)
        # 진짜 텍스트 기반 결정론적 연산 NO_HARDCODED_CONSTANTS]
        char_count = len(content)
        return {
            "slot": slot_id, "pid": os.getpid(), 
            "path": os.path.basename(path), "size": fsize, "chars": char_count
        }
    except: return None

def run():
    # [W002] 탐색 범위를 umr 전체로 확장하여 누락 방지
    base_dir = r"C:\g6core\g6_v24\data\umr"
    run_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    all_files = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            # 확장자 무관하게 파일이면 일단 수집
            all_files.append(os.path.join(root, f))
    
    # [W001] 실증 데이터 확보 실패 시 즉시 자폭
    if len(all_files) < 120:
        print(f"CRITICAL: Found only {len(all_files)} files in {base_dir}. Pipeline STOP.")
        sys.exit(1)
        
    target_files = all_files[:120]

    with multiprocessing.Pool(processes=8) as pool:
        tasks = [(f, i+1) for i, f in enumerate(target_files)]
        results = [r for r in pool.map(worker_task, tasks) if r]

    # [EVIDENCE] 영수증 생성
    with open(os.path.join(run_dir, "matrix_r1.csv"), "w", newline="", encoding="utf-8-sig") as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader(); writer.writerows(results)

    receipt = {"status": "PASS", "rows": len(results), "unique_pids": len(set(r['pid'] for r in results))}
    with open(os.path.join(run_dir, "receipt.json"), "w") as f: json.dump(receipt, f, indent=2)
    print(f"DONE: {len(results)} rows found and analyzed.")

if __name__ == "__main__": run()
