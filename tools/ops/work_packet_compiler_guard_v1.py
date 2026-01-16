import sys, os, json, csv
def validate():
    tsv_path, run_id = sys.argv[1], sys.argv[2]
    with open(tsv_path, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    
    # 통계적 실증 (EVIDENCE)
    lane_counts = {}
    real_work = 0
    for r in rows:
        lane_counts[r['lane']] = lane_counts.get(r['lane'], 0) + 1
        if r['kind'] in ['BUILD', 'PATCH', 'WIRE', 'DATA']: real_work += 1
    
    verdict = "PASS" if len(rows) == 120 and real_work >= 90 else "FAIL"
    report = {"verdict": verdict, "evidence": {"total_rows": len(rows), "real_work": real_work, "lanes": len(lane_counts)}}
    
    os.makedirs(f"runs/{run_id}", exist_ok=True)
    with open(f"runs/{run_id}/compile_guard_report.json", 'w') as f:
        json.dump(report, f, indent=4)
    if verdict == "FAIL": sys.exit(2)
if __name__ == "__main__": validate()
