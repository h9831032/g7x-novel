import os, sys, hashlib, argparse

def verify(run_dir):
    # [P0-017] 필수 파일 존재 및 크기 검사
    required = ["stdout.txt", "stderr.txt", "receipt.json", "hash_manifest.csv"]
    for f in required:
        p = os.path.join(run_dir, f)
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            print(f"FAIL_FAST: {f} is missing or empty")
            sys.exit(3)

    # [P0-018] 가라 데이터(SIMULATED) 탐지
    with open(os.path.join(run_dir, "hash_manifest.csv"), "r", encoding="utf-8", errors="ignore") as f:
        if "SIMULATED" in f.read().upper():
            print("FRAUD_DETECTED: Simulated hash string found in manifest!")
            sys.exit(4)
            
    print(f"VERIFICATION_SUCCESS: {run_dir}")
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_dir", required=True)
    verify(parser.parse_args().run_dir)
