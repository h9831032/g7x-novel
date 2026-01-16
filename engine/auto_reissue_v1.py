import os, json, shutil

ROOT = "C:\\g7core\\g7_v1"
FAIL_BOX_DIR = os.path.join(ROOT, "runs", "REAL", "FAIL_BOX")
SUMMARY_PATH = os.path.join(ROOT, "FINAL", "reissue_summary.json")

def scan_and_reissue():
    summary = {"reissued_count": 0, "split_count": 0, "details": []}
    if not os.path.exists(FAIL_BOX_DIR): return
    
    trucks = os.listdir(FAIL_BOX_DIR)
    for truck in trucks:
        bundles = os.listdir(os.path.join(FAIL_BOX_DIR, truck))
        for bundle in bundles:
            reason_path = os.path.join(FAIL_BOX_DIR, truck, bundle, "reason.json")
            with open(reason_path, 'r', encoding='utf-8') as f:
                reason = json.load(f)
            
            retry_count = reason.get("retry_count", 0)
            if retry_count == 0:
                # [RULE] 1회차: 6개 그대로 재시도
                summary["reissued_count"] += 1
                print(f">>> [REISSUE] {bundle} 1회차 (6-Bundle) 재발주")
            elif retry_count == 1:
                # [RULE] 2회차: 3+3 분해 재시도
                summary["split_count"] += 1
                print(f">>> [SPLIT] {bundle} 2회차 (3+3 분해) 재발주")
            else:
                print(f"!!! [FATAL] {bundle} 영구 FAIL 처리")
    
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=4)

if __name__ == "__main__":
    scan_and_reissue()