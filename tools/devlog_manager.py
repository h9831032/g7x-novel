# C:\g7core\g7_v1\tools\devlog_manager.py
import json, os, argparse

def audit_run(run_id):
    run_dir = os.path.join(r"C:\g7core\g7_v1\runs", run_id)
    audit_path = os.path.join(run_dir, "final_audit.json")
    
    if not os.path.exists(audit_path):
        print("[ERROR] final_audit.json not found."); return

    with open(audit_path, 'r') as f: audit = json.load(f)
    
    # 동적 PASS 판정
    verdict = "PASS" if audit["STAMP_COUNT"] == audit["TARGET"] else "FAIL"
    
    report = {
        "run_id": run_id,
        "target": audit["TARGET"],
        "stamps": audit["STAMP_COUNT"],
        "verdict": verdict,
        "outputs_count": len(os.listdir(os.path.join(run_dir, "outputs"))) if os.path.exists(os.path.join(run_dir, "outputs")) else 0
    }
    
    with open(os.path.join(run_dir, "verify_report.json"), 'w') as f: json.dump(report, f, indent=4)
    print(f"\n[AUDIT REPORT] RUN_ID: {run_id} | VERDICT: {verdict}")
    print(f"Stamps: {report['stamps']} / {report['target']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_id", required=True)
    audit_run(parser.parse_args().run_id)