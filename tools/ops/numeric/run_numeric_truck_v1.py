import sys, os, csv, json, hashlib, time
from concurrent.futures import ThreadPoolExecutor
def calc(r, run_id):
    with open(r['input_path'], 'r') as f: n = int(f.read().strip())
    add, mul, div, mod = n + 7, n * 13, (n * 13) // 13, (n * 13 + 7) % 97
    res = {"row_id": r['row_id'], "lane": r['lane'], "n": n, "add": add, "mul": mul, "div": div, "mod": mod, "input_path": r['input_path'], "output_path": r['output_path']}
    os.makedirs(os.path.dirname(r['output_path']), exist_ok=True)
    with open(r['output_path'], 'w') as f: json.dump(res, f)
    sig = hashlib.sha256(f"NUMERIC|{n}|{r['lane']}|{r['row_id']}|{run_id}".encode()).hexdigest()
    log_p = f"runs/{run_id}/lane_logs/lane{str(r['lane']).zfill(2)}.log"
    os.makedirs(os.path.dirname(log_p), exist_ok=True)
    with open(log_p, 'a') as l: l.write(f"{r['row_id']}\t{sig}\n")
    return f"{run_id},{r['row_id']},{r['lane']},NUMERIC_CALC|{n},{sig},{r['input_path']},{r['output_path']},0,1024,10"
def main():
    run_id = sys.argv[1]
    with open(f"runs/{run_id}/work_packet.tsv", 'r', encoding='utf-8-sig') as f: rows = list(csv.DictReader(f, delimiter='\t'))
    with ThreadPoolExecutor(max_workers=8) as exe: res = list(exe.map(lambda r: calc(r, run_id), rows))
    with open(f"runs/{run_id}/receipt.jsonl", 'w') as f: f.write("\n".join(res))
if __name__ == "__main__": main()
