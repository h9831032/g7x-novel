import os
import json
import hashlib
import sys
from datetime import datetime

def get_sha1(filepath):
    if not os.path.exists(filepath): return None
    with open(filepath, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()

def run_blackbox_audit():
    root = r"C:\g7core\g7_v1"
    real_path = os.path.join(root, "runs", "REAL")
    export_path = os.path.join(real_path, "MASTER_FINAL_EXPORT")
    
    # [A] Budget Guard Logic
    receipt_path = os.path.join(real_path, "api_receipt.jsonl")
    budget_log = os.path.join(real_path, "budget_guard.log")
    try:
        total_tokens = 0
        if os.path.exists(receipt_path):
            with open(receipt_path, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    total_tokens += data.get("usage", {}).get("total_tokens", 0)
            with open(budget_log, "w", encoding="utf-8") as f:
                f.write(f"TIMESTAMP: {datetime.now().isoformat()}\nTOTAL_TOKEN_CONSUMPTION: {total_tokens}")
    except Exception as e:
        return False, f"BudgetGuard Fail: {str(e)}"

    # [B] Check Essential Files
    required_files = {
        "verify_report": os.path.join(export_path, "verify_report.json"),
        "devlog": os.path.join(real_path, "DEVLOG", "devlog.jsonl"),
        "budget_log": budget_log,
        "state_a": os.path.join(real_path, "TRUCK_A", "FINAL", "state_pack.json"),
        "state_b": os.path.join(real_path, "TRUCK_B", "FINAL", "state_pack.json")
    }

    manifest = {}
    summary_lines = [f"--- G7X BLACKBOX SUMMARY ({datetime.now()}) ---"]
    
    for key, path in required_files.items():
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return False, f"Missing or Empty file: {path}"
        sha1 = get_sha1(path)
        manifest[key] = {"path": path, "sha1": sha1}
        summary_lines.append(f"{key}: OK | {sha1}")

    # [C] Write Results
    with open(os.path.join(export_path, "hash_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
    with open(os.path.join(export_path, "blackbox_summary.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))
        
    return True, "Success"

if __name__ == "__main__":
    success, msg = run_blackbox_audit()
    if not success:
        print(f"AUDIT_FAIL: {msg}")
        sys.exit(1)
    print("AUDIT_PASS")
    sys.exit(0)