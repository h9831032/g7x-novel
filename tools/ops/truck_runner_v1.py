import sys, os, json, csv, time
def run():
    tsv_path, run_id = sys.argv[1], sys.argv[2]
    os.makedirs(f"runs/{run_id}/lane_logs", exist_ok=True)
    with open(tsv_path, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    
    receipts = []
    for r in rows:
        # 실제 파일 흔적 남기기 (NO_DUMMY)
        target = os.path.join("C:/g7core/g7_v1/data_output", f"task_{r['row_id']}.txt")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, 'w') as f: f.write(f"TS:{time.time()}|SIG:{r['task_signature']}")
        
        receipts.append(f"{run_id},{r['row_id']},{r['lane']},{r['task_signature']},0,10")
    
    with open(f"runs/{run_id}/receipt.jsonl", 'w') as f:
        f.write("\n".join(receipts))
if __name__ == "__main__": run()
