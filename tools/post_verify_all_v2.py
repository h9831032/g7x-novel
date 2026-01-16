
import os
import json
import hashlib
import sys
from datetime import datetime

ROOT = r"C:\g7core\g7_v1"
EXPORT_DIR = os.path.join(ROOT, "runs", "REAL", "MASTER_FINAL_EXPORT")
REQUIRED_FILES = [
    r"runs\REAL\budget_guard.log",
    r"runs\REAL\api_receipt.jsonl",
    r"runs\REAL\DEVLOG\devlog.jsonl"
]

def calculate_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def run_verify():
    manifest = {}
    all_exist = True
    
    print(">>> [STAMPER] verifying physical artifacts...")
    
    for rel_path in REQUIRED_FILES:
        full_path = os.path.join(ROOT, rel_path)
        if not os.path.exists(full_path) or os.path.getsize(full_path) == 0:
            print(f"!!! [FAIL] Missing or Empty: {rel_path}")
            all_exist = False
            manifest[rel_path] = "MISSING"
        else:
            h = calculate_hash(full_path)
            manifest[rel_path] = h
            print(f"   [OK] {rel_path} | SHA: {h[:8]}...")

    # 결과 기록
    with open(os.path.join(EXPORT_DIR, "hash_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

    # [중요] 조건부 PASS - 무조건 PASS 금지
    verdict = "PASS" if all_exist else "FAIL"
    
    report = {
        "verdict": verdict,
        "timestamp": str(datetime.now()),
        "checked_files": len(REQUIRED_FILES)
    }
    
    with open(os.path.join(EXPORT_DIR, "verify_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    
    # Exit Code 설정
    with open(os.path.join(EXPORT_DIR, "exitcode.txt"), "w", encoding="utf-8") as f:
        f.write("0" if verdict == "PASS" else "1")

    if verdict == "FAIL":
        print(">>> [STAMPER] VERDICT: FAIL (Artifacts Missing)")
        sys.exit(1)
    else:
        print(">>> [STAMPER] VERDICT: PASS (Sealed)")
        sys.exit(0)

if __name__ == "__main__":
    run_verify()
