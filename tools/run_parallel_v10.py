import os
import json
import sys
import time
import random
import concurrent.futures
from pathlib import Path

# [CONFIG]
SSOT_ROOT = Path(r"C:\g7core\g7_v1")
TRUCK_NAME = sys.argv[1] if len(sys.argv) > 1 else "truckA"
RUN_DIR = SSOT_ROOT / "runs" / "REAL" / TRUCK_NAME
FAIL_BOX_DIR = RUN_DIR / "FAIL_BOX"

os.makedirs(RUN_DIR, exist_ok=True)
os.makedirs(FAIL_BOX_DIR, exist_ok=True)

def process_task(task_id, task_type):
    # Truck B 의도적 실패 지점: B_133, B_150 (테스트용)
    if task_id in ["B_133", "B_150"]:
        raise Exception(f"Intentional Failure for {task_id}")
    time.sleep(random.uniform(0.01, 0.05)) 
    return {"task_id": task_id, "type": task_type, "status": "SUCCESS"}

def run_bundle(bundle_idx):
    bundle_id = f"bundle_{bundle_idx:02d}"
    # Truck B일 경우 인덱스 오프셋 적용
    offset = 120 if TRUCK_NAME == "truckB" else 0
    start_num = offset + (bundle_idx - 1) * 6 + 1
    
    tasks = [(f"B_{start_num + i:03d}", "MID") for i in range(6)]
    results = []
    
    try:
        for t_id, t_type in tasks:
            results.append(process_task(t_id, t_type))
        
        with open(RUN_DIR / f"{bundle_id}_verify_report.json", "w") as f:
            json.dump({"bundle": bundle_id, "status": "PASS", "tasks": results}, f)
        return True
    except Exception as e:
        with open(FAIL_BOX_DIR / f"{bundle_id}_reason.json", "w") as f:
            json.dump({"bundle": bundle_id, "error": str(e)}, f)
        return False

def main():
    print(f"--- [PHASE-4 START] Target: {TRUCK_NAME} (120 Tasks) ---")
    completed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(run_bundle, i+1) for i in range(20)]
        for future in concurrent.futures.as_completed(futures):
            if future.result(): completed += 1
            
    with open(RUN_DIR / "ops_summary.json", "w") as f:
        json.dump({"truck": TRUCK_NAME, "completed_bundles": completed, "physical_count_ok": completed==20}, f)
    print(f"--- [PHASE-4 FINISHED] {TRUCK_NAME} Saved ---")

if __name__ == "__main__":
    main()