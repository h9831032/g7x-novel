import os, sys
AUDIT_DIR = r"C:\g7core\g7_v1\runs\audit"
FILES = ["verify_report.json", "hash_manifest.json", "exitcode.txt"]

def verify():
    print(">>> [V7_VERIFY] Final check...")
    for f in FILES:
        p = os.path.join(AUDIT_DIR, f)
        if not os.path.exists(p) or os.path.getsize(p) < 1:
            print(f"  [FAIL] {f} missing or empty."); sys.exit(1)
        print(f"  [OK] {f} verified.")
    print(">>> [SUCCESS] All V6/V7 deliverables confirmed.")

if __name__ == "__main__":
    verify()