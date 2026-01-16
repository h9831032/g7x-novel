import os, sys
def verify(run_dir):
    files = ["compile_log.json", "receipt.json", "topN_candidates.json", "stdout.txt"]
    for f in files:
        if not os.path.exists(os.path.join(run_dir, f)):
            print(f"FAIL: {f} missing")
            sys.exit(1)
    print("VERIFY_PASS")
if __name__ == "__main__": verify(sys.argv[1])
