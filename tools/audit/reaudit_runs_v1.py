import os, json, csv, glob

def audit():
    root = r"C:\g7core\g7_v1\runs"
    report = []
    for run_dir in glob.glob(os.path.join(root, "*")):
        if not os.path.isdir(run_dir): continue
        reasons = []
        matrix_p = os.path.join(run_dir, "matrix_r1.csv")
        receipt_p = os.path.join(run_dir, "receipt.json")
        
        if not os.path.exists(matrix_p): reasons.append("MISSING_MATRIX")
        else:
            with open(matrix_p, 'r', encoding='utf-8-sig') as f:
                rows = list(csv.DictReader(f))
                if len(rows) > 0:
                    # [W001] 고정 점수(가라) 체크
                    s09_vals = [r.get('S09', r.get('S09_repeat')) for r in rows]
                    if len(set(s09_vals)) == 1: reasons.append("CONSTANT_SENSOR_FAKE")
                    # [W001] 고정 법전(가라) 체크
                    law_vals = [r.get('law_flags', '') for r in rows]
                    if len(set(law_vals)) == 1 and law_vals[0] != '': reasons.append("CONSTANT_LAW_FAKE")
        
        status = "FAKE_PASS_OVERRULED" if reasons else "PASS"
        report.append({"run_dir": os.path.basename(run_dir), "status": status, "fail_reasons": "|".join(reasons)})

    with open(os.path.join(root, "reaudited_runs_report.csv"), "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["run_dir", "status", "fail_reasons"])
        writer.writeheader(); writer.writerows(report)
    print(f"AUDIT_DONE: {len(report)} runs re-evaluated.")

if __name__ == "__main__": audit()
