# C:\g7core\g7_v1\tools\finalize_evidence_pack_v1.py
import os, json, argparse, datetime

def finalize(run_dir):
    report_path = os.path.join(run_dir, "verify_report.json")
    # [DoD] 증거팩 체크리스트 충족 여부 확인
    evidence_files = ["api_receipt.jsonl", "blackbox_log.jsonl", "stamp_manifest.json", "final_audit.json"]
    missing = [f for f in evidence_files if not os.path.exists(os.path.join(run_dir, f))]
    
    summary = {
        "run_id": os.path.basename(run_dir),
        "final_status": "PASS" if not missing else "FAIL",
        "missing_evidence": missing,
        "sealed_at": datetime.datetime.now().isoformat()
    }
    
    with open(os.path.join(run_dir, "sealed_evidence_bundle.json"), "w") as f:
        json.dump(summary, f, indent=4)
    print(f">>> EVIDENCE PACK SEALED: {summary['final_status']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_dir", required=True)
    args = parser.parse_args()
    finalize(args.run_dir)