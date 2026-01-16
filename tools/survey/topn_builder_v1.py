import csv
import json
import sys
import glob
import os

def build_targets(run_dir, top_n=50):
    files = glob.glob(os.path.join(run_dir, "matrix_r*.csv"))
    all_rows = []
    
    for f in files:
        with open(f, 'r', encoding='utf-8-sig', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # 점수 파싱 (S12 기준 내림차순 정렬 예시)
                try:
                    s12 = float(row.get('S12') or row.get('S12_stagnation') or 0)
                    row['score'] = s12
                    all_rows.append(row)
                except: continue

    # Score 기준 정렬 (높을수록 이상 징후)
    all_rows.sort(key=lambda x: x['score'], reverse=True)
    top_candidates = all_rows[:top_n]
    
    # 1. topN_candidates.json 저장
    with open(os.path.join(run_dir, "topN_candidates.json"), "w", encoding='utf-8') as f:
        json.dump(top_candidates, f, indent=2, ensure_ascii=False)

    # 2. label_queue.jsonl 저장 (사람/API가 라벨링할 큐)
    queue_path = os.path.join(run_dir, "label_queue.jsonl")
    with open(queue_path, "w", encoding='utf-8') as f:
        for item in top_candidates:
            task = {
                "block_id": f"{item.get('WID')}_{item.get('window_id')}",
                "score": item['score'],
                "human_label": None, # 추후 입력
                "api_label": None    # 추후 입력
            }
            f.write(json.dumps(task, ensure_ascii=False) + "\n")
            
    print(f"Top-{top_n} Candidates Extracted & Queued.")

if __name__ == "__main__":
    build_targets(sys.argv[1], 50)
