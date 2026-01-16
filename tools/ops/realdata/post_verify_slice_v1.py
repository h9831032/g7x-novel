import sys, os, json, hashlib
def verify():
    run_id = sys.argv[1]
    run_dir = f"runs/{run_id}"
    with open(f"{run_dir}/receipt.jsonl", 'r') as f: lines = f.readlines()
    errs = []
    if len(lines) != 120: errs.append("COUNT_MISMATCH")
    manifest = []
    for root, _, files in os.walk(run_dir):
        for fn in files:
            p = os.path.join(root, fn); h = hashlib.sha256()
            with open(p, 'rb') as fb:
                for chunk in iter(lambda: fb.read(8192), b""): h.update(chunk)
            manifest.append(f"{os.path.relpath(p, run_dir)},{os.path.getsize(p)},{h.hexdigest()}")
    os.makedirs(f"{run_dir}/post_verify", exist_ok=True)
    with open(f"{run_dir}/post_verify/hash_manifest.txt", 'w') as f: f.write("\n".join(manifest))
    with open(f"{run_dir}/post_verify/verify_report.json", 'w') as f:
        json.dump({"verdict": "PASS" if not errs else "FAIL", "meta": {"run_id": run_id, "rows": 120}}, f, indent=4)
if __name__ == "__main__": verify()
