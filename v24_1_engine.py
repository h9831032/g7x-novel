import os, json, csv, sys

def run(prev_run, run_dir):
    # [W119] 물리적 파일 존재 여부 선제적 체크
    matrix_p = os.path.join(prev_run, "rot_3", "matrix_r1.csv")
    if not os.path.exists(matrix_p):
        print(f"FATAL: Missing evidence file at {matrix_p}"); sys.exit(1)

    with open(matrix_p, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    
    # 상위 50개 선별 및 판결
    sorted_rows = sorted(rows, key=lambda x: float(x.get('score', 0)), reverse=True)[:50]
    
    verdicts = [{"id": r['row_id'], "sha1": r['sha1'], "verdict": "CONVICTED"} for r in sorted_rows]

    with open(os.path.join(run_dir, "topN_candidates.json"), "w", encoding='utf-8') as f:
        json.dump(verdicts, f, ensure_ascii=False, indent=2)

    print("JUDGE_SUCCESS")

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
