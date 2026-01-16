import os
import json
import time
from datetime import datetime
from pathlib import Path
import argparse

# [SSOT_ROOT_POLICY]
SSOT_ROOT = Path(r"C:\g7core\g7_v1")
FINAL_ROOT = SSOT_ROOT / "FINAL"
RUN_ROOT = SSOT_ROOT / "runs" / "REAL"

class FactoryBlackboxV11:
    def __init__(self, truck_id):
        self.run_id = f"RUN_{int(time.time())}"
        self.truck_id = truck_id
        self.truck_dir = RUN_ROOT / truck_id
        self.final_dir = self.truck_dir / "FINAL"
        self.error_box = self.truck_dir / "ERROR_BOX"
        self.state_path = self.final_dir / "state_pack.json"
        
        for d in [self.final_dir, self.error_box, FINAL_ROOT]:
            os.makedirs(d, exist_ok=True)
        self.state = self.load_state()

    def load_state(self):
        # [ROBUST_LOAD] 기본값 설정 후 기존 파일 병합
        defaults = {
            "run_id": self.run_id,
            "last_bundle": None,
            "auto_reissue_queue": [],
            "budget_link": str(self.final_dir / "budget_report.json")
        }
        if self.state_path.exists():
            try:
                with open(self.state_path, "r") as f:
                    data = json.load(f)
                    defaults.update(data) # 기존 데이터로 덮어쓰기 (KeyError 방지)
            except: pass
        return defaults

    def save_state(self):
        with open(self.state_path, "w") as f:
            json.dump(self.state, f, indent=4)

    def weld_and_report(self, bundle_id, status, tasks, budget_info):
        timestamp = datetime.now().isoformat()
        verify_data = {"run_id": self.run_id, "bundle_id": bundle_id, "pass_seal": status == "PASS", "tasks": tasks}
        with open(self.final_dir / f"{bundle_id}_verify.json", "w") as f:
            json.dump(verify_data, f, indent=4)

        if status == "FAIL":
            if bundle_id not in self.state["auto_reissue_queue"]:
                self.state["auto_reissue_queue"].append(bundle_id)
        elif status == "PASS" and bundle_id in self.state.get("auto_reissue_queue", []):
            self.state["auto_reissue_queue"].remove(bundle_id)

        self.state["last_bundle"] = bundle_id
        self.save_state()

        devlog_path = FINAL_ROOT / f"devlog_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(devlog_path, "a") as f:
            log_entry = {"timestamp": timestamp, "run_id": self.run_id, "bundle": bundle_id, "result": status}
            f.write(json.dumps(log_entry) + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--truck", required=True)
    parser.add_argument("--mode", default="INTEGRATION", choices=["INTEGRATION", "REISSUE"])
    args = parser.parse_args()

    blackbox = FactoryBlackboxV11(args.truck)

    if args.mode == "REISSUE":
        targets = list(blackbox.state.get("auto_reissue_queue", []))
        for bundle_id in targets:
            tasks = [{"id": f"RE_{bundle_id}_{j}", "op": "WELD_FIX"} for j in range(6)]
            blackbox.weld_and_report(bundle_id, "PASS", tasks, {"tokens": 1200, "recovery": True})
    else:
        print(f"--- [FACTORY_V11_REPAIRED] Mode: {args.mode} ---")
        for i in range(1, 21):
            bundle_id = f"bundle_{i:02d}"
            print(f">>> Processing {bundle_id}...")
            tasks = [{"id": f"T_{i}_{j}", "op": "WELD"} for j in range(6)]
            blackbox.weld_and_report(bundle_id, "PASS", tasks, {"tokens": 1500})
        print(f"--- [FACTORY_V11_COMPLETE] ---")

if __name__ == "__main__":
    main()