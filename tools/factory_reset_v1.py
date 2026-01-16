import os, shutil, glob

ROOT = r"C:\g7core\g7_v1"
PATHS = [
    os.path.join(ROOT, "queue", "work_orders"),
    os.path.join(ROOT, "runs", "audit"),
    os.path.join(ROOT, "runs", "REAL", "DEVLOG"),
    os.path.join(ROOT, "runs", "REAL", "api_receipt.jsonl")
]

def reset():
    print(">>> [RESET] Cleaning...")
    for p in PATHS:
        try:
            if os.path.isfile(p): os.remove(p)
            elif os.path.isdir(p):
                for f in glob.glob(os.path.join(p, "*")):
                    try: os.remove(f)
                    except: shutil.rmtree(f, ignore_errors=True)
            print(f"  [OK] Cleaned {os.path.basename(p)}")
        except Exception as e:
            print(f"  [SKIP] {os.path.basename(p)}: {e}")

if __name__ == "__main__":
    reset()