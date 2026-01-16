import os, json, hashlib

def write_evidence(run_id):
    root = r"C:\g7core\g7_v1"
    run_dir = os.path.join(root, "runs", run_id)
    report_path = os.path.join(run_dir, "evidence_pack.txt")
    
    content = [f"=== G7X EVIDENCE PACK: {run_id} ===", ""]
    
    for t_id in ["A", "B"]:
        final_path = os.path.join(run_dir, f"truck{t_id}", "FINAL", "truck_verify_report.json")
        if os.path.exists(final_path):
            with open(final_path, 'r') as f:
                data = json.load(f)
                content.append(f"[Truck {t_id}] PASS_SEAL: {data['pass_seal']}, Bundles: {data['bundles']}, Sigs: {data['sigs']}")
        else:
            content.append(f"[Truck {t_id}] NO_FINAL_REPORT_FOUND")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(content))
    
    # 자가 해시 생성
    with open(report_path, 'rb') as f:
        sig = hashlib.sha256(f.read()).hexdigest()
    with open(os.path.join(run_dir, "evidence_pack.hash_manifest.json"), 'w') as f:
        json.dump({"evidence_pack.txt": sig}, f)
    
    print(f"### [EVIDENCE] Pack sealed at {report_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1: write_evidence(sys.argv[1])