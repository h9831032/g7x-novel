import sys, os, csv, time, shutil
from concurrent.futures import ThreadPoolExecutor
def run_task(r, run_id):
    try:
        os.makedirs(os.path.dirname(r['output_path']), exist_ok=True)
        start = time.time()
        shutil.copy2(r['input_path'], r['output_path'])
        dur = int((time.time() - start) * 1000)
        size = os.path.getsize(r['output_path'])
        log_p = f"runs/{run_id}/lane_logs/lane{r['lane'].zfill(2)}.log"
        os.makedirs(os.path.dirname(log_p), exist_ok=True)
        with open(log_p, 'a', encoding='utf-8') as l: 
            l.write(f"{r['row_id']}\t{r['task_signature']}\t{dur}ms\n")
        return f"{run_id},{r['row_id']},{r['lane']},{r['task_signature']},0,{size},{dur}"
    except Exception as e:
        return f"{run_id},{r['row_id']},{r['lane']},{r['task_signature']},1,0,0"

def main():
    tsv, run_id = sys.argv[1], sys.argv[2]
    with open(tsv, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    with ThreadPoolExecutor(max_workers=8) as exe:
        res = list(exe.map(lambda r: run_task(r, run_id), rows))
    os.makedirs(f"runs/{run_id}", exist_ok=True)
    with open(f"runs/{run_id}/receipt.jsonl", 'w', encoding='utf-8') as f:
        f.write("\n".join(res))
if __name__ == "__main__": main()
