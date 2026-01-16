import sys, os, csv, json, hashlib, time
from concurrent.futures import ThreadPoolExecutor
def run_task(r, run_id):
    with open(r['input_path'], 'rb') as f: data = f.read(1024)
    payload = {"row_id": r['row_id'], "slot": r['slot'], "key": r['semantic_dup_key'], "data_size": len(data)}
    os.makedirs(os.path.dirname(r['output_path']), exist_ok=True)
    with open(r['output_path'], 'w') as f: json.dump(payload, f)
    log_p = f"runs/{run_id}/lane_logs/lane{str(r['lane']).zfill(2)}.log"
    os.makedirs(os.path.dirname(log_p), exist_ok=True)
    with open(log_p, 'a') as l: 
        l.write(f"ROW:{r['row_id']}\tSIG:{hashlib.sha1(r['semantic_dup_key'].encode()).hexdigest()}\n")
    return f"{run_id},{r['row_id']},{r['lane']},0"
def main():
    run_id = sys.argv[1]
    with open(f"runs/{run_id}/work_packet.tsv", 'r', encoding='utf-8-sig') as f: rows = list(csv.DictReader(f, delimiter='\t'))
    with ThreadPoolExecutor(max_workers=8) as exe: list(exe.map(lambda r: run_task(r, run_id), rows))
if __name__ == "__main__": main()
