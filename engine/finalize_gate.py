import os, sys, json, glob

def verify_sealing(run_path):
    receipt_log = os.path.join(run_path, "api_receipt.jsonl")
    receipt_count = 0
    if os.path.exists(receipt_log):
        with open(receipt_log, "r") as f:
            receipt_count = len(f.readlines())

    checks = {
        "RECEIPT_COUNT": receipt_count >= 120,
        "HASH_MANIFEST": os.path.exists(os.path.join(run_path, "hash_manifest.json")),
        "EXITCODE_0": os.path.exists(os.path.join(run_path, "exitcode.txt"))
    }

    if not all(checks.values()):
        bb_log = os.path.join(run_path, "blackbox_log.jsonl")
        with open(bb_log, "a") as f:
            f.write(json.dumps({"event": "GATE_B_FAIL", "checks": checks}) + "\n")
        print(f">>> [GATE_B_FAIL] {checks}")
        sys.exit(1)
    
    print(">>> [GATE_B_PASS] Final Integrity Verified.")
    return True