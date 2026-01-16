import os
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# [SSOT_ROOT_POLICY]
SSOT_ROOT = Path(r"C:\g7core\g7_v1")
FINAL_ROOT = SSOT_ROOT / "FINAL"
RUN_ROOT = SSOT_ROOT / "runs" / "REAL"

# [MANDATORY_WELD_RULES]
class FactoryBlackbox:
    def __init__(self, truck_id):
        self.run_id = f"RUN_{int(time.time())}"
        self.truck_id = truck_id
        self.truck_dir = RUN_ROOT / truck_id
        self.final_dir = self.truck_dir / "FINAL"
        self.error_box = self.truck_dir / "ERROR_BOX"
        
        for d in [self.final_dir, self.error_box, FINAL_ROOT]:
            os.makedirs(d, exist_ok=True)

    def weld_and_report(self, bundle_id, status, tasks, budget_info):
        timestamp = datetime.now().isoformat()
        
        # 1. VERIFY_REPORT
        verify_data = {
            "run_id": self.run_id,
            "bundle_id": bundle_id,
            "pass_seal": status == "PASS",
            "tasks": tasks
        }
        verify_path = self.final_dir / f"{bundle_id}_verify.json"
        with open(verify_path, "w") as f:
            json.dump(verify_data, f, indent=4)

        # 2. BUDGET_REPORT
        budget_path = self.final_dir / "budget_report.json"
        with open(budget_path, "w") as f:
            json.dump({"run_id": self.run_id, "cost": budget_info}, f, indent=4)

        # 3. STATE_PACK (Resume Enable)
        state_data = {
            "last_bundle": bundle_id,
            "resume_command": f"python engine\\run_factory_v10.py --truck {self.truck_id} --resume_from {bundle_id}",
            "auto_reissue_queue": [] if status == "PASS" else [bundle_id],
            "budget_link": str(budget_path)
        }
        with open(self.final_dir / "state_pack.json", "w") as f:
            json.dump(state_data, f, indent=4)

        # 4. DEVLOG (Integration Map)
        devlog_path = FINAL_ROOT / f"devlog_{datetime.now().strftime('%Y%m%d')}.jsonl"
        log_entry = {
            "timestamp": timestamp,
            "run_id": self.run_id,
            "bundle": bundle_id,
            "result": status,
            "error_link": str(self.error_box) if status != "PASS" else None
        }
        with open(devlog_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--truck", required=True)
    parser.add_argument("--mode", default="INTEGRATION")
    args = parser.parse_args()

    blackbox = FactoryBlackbox(args.truck)
    print(f"--- [FACTORY_WELD_START] ID: {blackbox.run_id} ---")

    # 통합 가동 시뮬레이션 (6x20=120)
    for i in range(1, 21):
        bundle_id = f"bundle_{i:02d}"
        print(f">>> Processing {bundle_id}...")
        
        # 가상 태스크 생산
        tasks = [{"id": f"T_{i}_{j}", "op": "WELD"} for j in range(6)]
        
        # 의도적 결함 테스트 (PHASE-4 규칙)
        status = "PASS" if i != 7 else "FAIL" 
        
        budget_mock = {"tokens": 1500, "cost_usd": 0.002}
        blackbox.weld_and_report(bundle_id, status, tasks, budget_mock)
        
        if status == "FAIL":
            print(f"!!! {bundle_id} FAILED -> ERROR_BOX LOGGED")

    print(f"--- [FACTORY_WELD_COMPLETE] Check FINAL/ directory ---")

if __name__ == "__main__":
    main()