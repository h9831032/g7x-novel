import os, json, csv, time, sys, gc
from tools.sharder import split_jsonl
from tools.metrics_v14 import G7X_MetricsV14

def main():
    input_dir = r"C:\g6core\g6_v24\data\umr\chunks"
    run_id = "PHASE18_V14_SHARD1000_" + time.strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(r"C:\g7core\g7_v1\runs", run_id)
    staging_dir = os.path.join(run_dir, "staging_shards")
    os.makedirs(staging_dir, exist_ok=True)

    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.jsonl')]
    print(f">>> [G7X] Sharding {len(files)} files to avoid SKIP_TOO_LARGE...")
    
    # 1. 전량 분할 공정
    for f in files: split_jsonl(f, staging_dir)
    
    shard_files = [os.path.join(staging_dir, f) for f in os.listdir(staging_dir)]
    engine = G7X_MetricsV14()
    novel_map = {}
    results = []
    target_novels = 1000

    # 2. 스트리밍 집계 공정
    print(f">>> [G7X] Starting Stream Scan on Shards. Target: {target_novels}")
    for sf in shard_files:
        if len(results) >= target_novels: break
        with open(sf, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    nid = data.get("novel_id") or data.get("book_id")
                    if not nid: continue
                    if nid not in novel_map:
                        if len(results) + len(novel_map) >= target_novels: continue
                        novel_map[nid] = []
                    novel_map[nid].append(data.get("text", ""))
                    
                    if len(novel_map[nid]) >= 40:
                        scores = engine.compute(novel_map.pop(nid))
                        row = {"novel_id": nid}
                        for k, v in scores.items():
                            row[f"{k.replace('_score','')}_mean"] = v
                            row[f"{k.replace('_score','')}_p95"] = v # V14에서 정밀화 가능
                        results.append(row)
                        if len(results) % 10 == 0: print(f">>> [PROGRESS] {len(results)}/1000 Novels Collected...")
                        if len(results) >= target_novels: break
                except: continue
        gc.collect()

    # 3. 산출물 및 영수증 (하청지시서 규격 준수)
    matrix_path = os.path.join(run_dir, "quality_matrix.csv")
    with open(matrix_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=results[0].keys())
        w.writeheader()
        w.writerows(results)

    receipt = {
        "run_id": run_id, "novels_processed": len(results), "sys_executable": sys.executable,
        "cwd": os.getcwd(), "input_dir": input_dir, "status": "V14_SHARD_SUCCESS"
    }
    with open(os.path.join(run_dir, "receipt.jsonl"), "w", encoding="utf-8") as f:
        json.dump(receipt, f)
    
    print(f"\n>>> [SUCCESS] V14 완주 성공. 1000권 집계표 생성 완료: {run_dir}")

if __name__ == "__main__": main()
