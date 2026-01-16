import os, json, csv, statistics, sys, glob
def run_audit():
    try:
        root = r"C:\g7core\g7_v1"
        runs_dir = os.path.join(root, "runs")
        run_folders = [os.path.join(runs_dir, d) for d in os.listdir(runs_dir) if "CHUNK_NATIVE_REAL" in d]
        if not run_folders: raise Exception("NO_RUN_FOLDERS")
        latest_run = max(run_folders, key=os.path.getmtime)
        
        matrix_files = glob.glob(os.path.join(latest_run, "matrix_r*.csv"))
        all_data = []
        scores = []
        for f_path in matrix_files:
            with open(f_path, "r", encoding="utf-8-sig", errors="ignore") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    val = float(row.get("S12") or row.get("S12_stagnation") or 0)
                    row["score"] = val
                    scores.append(val)
                    all_data.append(row)
        
        baseline = {"S12": {"mean": round(statistics.mean(scores), 4), "p95": round(sorted(scores)[int(len(scores)*0.95)], 4)}}
        with open(os.path.join(latest_run, "baseline_stats.json"), "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2)
            
        all_data.sort(key=lambda x: x["score"], reverse=True)
        with open(os.path.join(latest_run, "topN_candidates.json"), "w", encoding="utf-8") as f:
            json.dump(all_data[:50], f, indent=2, ensure_ascii=False)
            
        print(f"SUCCESS: {len(all_data)} rows analyzed in {os.path.basename(latest_run)}")
    except Exception as e:
        print(f"PYTHON_FAIL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_audit()
