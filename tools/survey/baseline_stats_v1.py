import csv
import json
import statistics
import sys
import glob
import os

def calculate_baseline(run_dir):
    # 모든 matrix_r*.csv 병합 로드
    files = glob.glob(os.path.join(run_dir, "matrix_r*.csv"))
    if not files:
        print("CRITICAL: No matrix CSV files found.")
        sys.exit(1)

    data = {"S01": [], "S12": []} # 센서 확장 가능
    
    row_count = 0
    for f in files:
        with open(f, 'r', encoding='utf-8-sig', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    if 'S01' in row and row['S01']: data["S01"].append(float(row['S01']))
                    if 'S12_stagnation' in row and row['S12_stagnation']: data["S12"].append(float(row['S12_stagnation']))
                    elif 'S12' in row and row['S12']: data["S12"].append(float(row['S12'])) # 컬럼명 호환
                    row_count += 1
                except ValueError: continue

    stats = {}
    for sensor, values in data.items():
        if not values:
            stats[sensor] = "NO_DATA"
            continue
        stats[sensor] = {
            "count": len(values),
            "mean": round(statistics.mean(values), 4),
            "std_dev": round(statistics.stdev(values), 4) if len(values) > 1 else 0,
            "p05": round(sorted(values)[int(len(values)*0.05)], 4),
            "p50": round(statistics.median(values), 4),
            "p95": round(sorted(values)[int(len(values)*0.95)], 4)
        }
    
    # 결과 저장
    with open(os.path.join(run_dir, "baseline_stats.json"), "w", encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Baseline Calculated from {row_count} rows.")

if __name__ == "__main__":
    calculate_baseline(sys.argv[1])
