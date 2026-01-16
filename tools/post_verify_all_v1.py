import os
import sys
import json
from datetime import datetime

def post_verify_all(base_path):
    master_dir = os.path.join(base_path, "MASTER_FINAL_EXPORT")
    os.makedirs(master_dir, exist_ok=True)
    
    trucks = ["A", "B"]
    total_actual = 0
    reports = {}

    for t in trucks:
        # run_integrated_v11.py에서 truck_id를 "A", "B"로 줬으므로 폴더명은 A, B임
        report_path = os.path.join(base_path, t, "verify_report.json")
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                total_actual += data.get("actual", 0)
                reports[t] = data
        else:
            reports[t] = "MISSING"

    master_report = {
        "timestamp": datetime.now().isoformat(),
        "expected_total": 240,
        "actual_total": total_actual,
        "truck_details": reports,
        "verdict": "PASS" if total_actual == 240 else "FAIL"
    }

    # 마스터 리포트 및 요약 파일 생성
    with open(os.path.join(master_dir, "verify_report.json"), "w", encoding="utf-8") as f:
        json.dump(master_report, f, indent=4)
    
    with open(os.path.join(base_path, "ops_summary.json"), "w", encoding="utf-8") as f:
        json.dump({"verdict": master_report["verdict"], "total": total_actual}, f, indent=4)

    print(f">>> MASTER_FINAL_EXPORT generated at {master_dir}")
    print(f">>> Final Verdict: {master_report['verdict']} ({total_actual}/240)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        post_verify_all(sys.argv[1])