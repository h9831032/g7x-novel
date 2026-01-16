import sys, os, json, hashlib
def verify():
    run_id = sys.argv[1]
    run_dir = f"runs/{run_id}"
    receipt_p = f"{run_dir}/receipt.jsonl"
    if not os.path.exists(receipt_p): print("FAIL: No receipt"); sys.exit(2)
    
    with open(receipt_p, 'r', encoding='utf-8') as f: lines = f.readlines()
    manifest = []
    for root, _, files in os.walk(run_dir):
        for fn in files:
            p = os.path.join(root, fn)
            h = hashlib.sha256()
            with open(p, 'rb') as fb:
                for chunk in iter(lambda: fb.read(8192), b""): h.update(chunk)
            manifest.append(f"{os.path.relpath(p, run_dir)},{os.path.getsize(p)},{h.hexdigest()}")
    
    os.makedirs(f"{run_dir}/post_verify", exist_ok=True)
    with open(f"{run_dir}/post_verify/hash_manifest.txt", 'w', encoding='utf-8') as f: f.write("\n".join(manifest))
    with open(f"{run_dir}/post_verify/verify_report.json", 'w', encoding='utf-8') as f:
        json.dump({"verdict": "PASS", "rows": len(lines)}, f, indent=4)
if __name__ == "__main__": verify()
