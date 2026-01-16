import sys, os, json, hashlib
def verify():
    run_id = sys.argv[1]
    run_dir = f"runs/{run_id}"
    sums = {"n":0, "add":0, "mul":0, "div":0, "mod":0}
    for i in range(1, 121):
        with open(f"{run_dir}/payload/row_{str(i).zfill(3)}.json", 'r') as f:
            d = json.load(f)
            for k in sums: sums[k] += d[k]
            if d['add'] != d['n']+7 or d['div'] != d['n']: sys.exit(2)
    verdict = "PASS" if len(os.listdir(f"{run_dir}/lane_logs")) == 8 else "FAIL"
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
        json.dump({"verdict": verdict, "meta": {"run_id": run_id, "rows": 120}, "sums": sums}, f, indent=4)
if __name__ == "__main__": verify()
