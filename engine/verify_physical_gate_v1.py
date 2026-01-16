import os
import sys
import json

def verify_gate(truck_path, expected_count=120):
    report_path = os.path.join(truck_path, "verify_report.json")
    if not os.path.exists(report_path):
        print("FAIL: verify_report.json missing")
        sys.exit(1)
        
    with open(report_path, "r") as f:
        data = json.load(f)
        
    if data.get("actual") != expected_count:
        print(f"FAIL: Physical count mismatch. Expected {expected_count}, got {data.get('actual')}")
        sys.exit(1)
        
    print(f"PASS: Physical gate cleared for {truck_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        verify_gate(sys.argv[1])