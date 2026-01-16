import os, sys, json, hashlib

ROOT_PATH = r"C:\g7core\g7_v1"

def internal_verify(b_dir):
    manifest_path = os.path.join(b_dir, "hash_manifest.json")
    if not os.path.exists(manifest_path): return False
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    # [V33.4] 단순화된 해시 구조 검증 (KeyError 방지)
    for f_name, saved_hash in manifest.items():
        f_path = os.path.join(b_dir, f_name)
        if not os.path.exists(f_path): return False
        with open(f_path, "rb") as f:
            curr_hash = hashlib.sha256(f.read()).hexdigest()
        if curr_hash != saved_hash: return False
    return True

def run_verify():
    try:
        run_id, truck_id = sys.argv[1:3]
        t_dir = os.path.join(ROOT_PATH, "runs", run_id, f"truck{truck_id}")
        bundles = sorted([d for d in os.listdir(t_dir) if d.startswith("bundle_")])
        sigs = set(); pass_count = 0

        for b_id in bundles:
            b_dir = os.path.join(t_dir, b_id)
            if internal_verify(b_dir):
                with open(os.path.join(b_dir, "verify_report.json"), "r") as f:
                    if json.load(f).get("pass_seal"):
                        pass_count += 1
                        with open(os.path.join(b_dir, "bundle_packet.jsonl"), "r") as p:
                            for line in p: sigs.add(json.loads(line).get("task_signature"))

        # 20개 번들 완주 확인
        is_pass = (pass_count == 20)
        final_dir = os.path.join(t_dir, "FINAL")
        os.makedirs(final_dir, exist_ok=True)
        
        with open(os.path.join(final_dir, "truck_verify_report.json"), "w") as f:
            json.dump({"pass_seal": is_pass, "bundles": pass_count, "sigs": len(sigs)}, f, indent=4)
        with open(os.path.join(final_dir, "exitcode.txt"), "w") as f:
            f.write("0" if is_pass else "2")
        
        print(f">>> [VERIFIER] 6x20 SERIAL AUDIT PASS: {is_pass} ({pass_count}/20)")
        sys.exit(0 if is_pass else 2)
    except Exception as e:
        print(f"!!! [VERIFY_ERR] {str(e)}")
        sys.exit(2)

if __name__ == "__main__": run_verify()