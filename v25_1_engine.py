import os, json, csv, sys

def run(prev_run, run_dir):
    # [W119] 물리 파일 존재 확인
    csv_path = os.path.join(prev_run, "rot_3", "matrix_r1.csv")
    if not os.path.exists(csv_path):
        print(f"ERROR: File not found at {csv_path}"); return False

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = [h.strip().lower() for h in reader.fieldnames]
        rows = list(reader)

    # [SCHEMA_AUDIT] 헤더가 형님의 기대와 다른지 체크
    print(f"RECEIPT: Detected Headers -> {headers}")
    
    if 'sha1' not in headers:
        print("ERROR: 'sha1' column is missing. Previous step failed to produce valid hash."); return False

    # 상위 20개 판결
    verdicts = []
    for r in rows[:20]:
        verdicts.append({
            "id": r.get('row_id') or r.get('chunk_id') or "N/A",
            "sha1": r.get('sha1'),
            "verdict": "CONVICTED"
        })

    with open(os.path.join(run_dir, "topN_candidates.json"), "w", encoding='utf-8') as f:
        json.dump(verdicts, f, ensure_ascii=False, indent=2)
    
    print("ENGINE_SUCCESS")
    return True

if __name__ == "__main__":
    success = run(sys.argv[1], sys.argv[2])
    if not success: sys.exit(1)
