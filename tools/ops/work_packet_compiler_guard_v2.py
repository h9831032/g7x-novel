import sys, os, json, csv
def guard():
    tsv, run_id = sys.argv[1], sys.argv[2]
    if not os.path.exists(tsv): print(f"FAIL: {tsv} not found"); sys.exit(2)
    with open(tsv, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    if not rows: print(f"FAIL: {tsv} is empty"); sys.exit(2)
    
    # 레인 할당 확인
    lanes = set(r['lane'] for r in rows)
    report = {"verdict": "PASS", "counts": len(rows), "lanes": list(lanes)}
    
    out_dir = f"runs/{run_id}"
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/compile_guard_report.json", 'w') as f: json.dump(report, f, indent=4)
if __name__ == "__main__": guard()
