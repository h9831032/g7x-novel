import sys, os, csv, json, hashlib, shutil, time
from concurrent.futures import ThreadPoolExecutor
def migrate(r, run_id):
    os.makedirs(os.path.dirname(r['output_path']), exist_ok=True)
    shutil.copy2(r['input_path'], r['output_path'])
    h = hashlib.sha256()
    with open(r['output_path'], 'rb') as fb:
        for chunk in iter(lambda: fb.read(65536), b""): h.update(chunk)
    sha256 = h.hexdigest()
    log_p = f"runs/{run_id}/lane_logs/lane{str(r['lane']).zfill(2)}.log"
    os.makedirs(os.path.dirname(log_p), exist_ok=True)
    with open(log_p, 'a', encoding='utf-8') as l:
        l.write(f"{r['row_id']}\t{r['filename']}\t{sha256}\n")
    return f"{run_id},{r['row_id']},{r['lane']},MIGRATE|{r['filename']},{sha256},{r['input_path']},{r['output_path']},0,0,0"

def main():
    run_id = sys.argv[1]
    with open(f"runs/{run_id}/work_packet.tsv", 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    with ThreadPoolExecutor(max_workers=8) as exe:
        res = list(exe.map(lambda r: migrate(r, run_id), rows))
    with open(f"runs/{run_id}/receipt.jsonl", 'w', encoding='utf-8') as f: f.write("\n".join(res))
if __name__ == "__main__": main()
