import sys, os, csv, json, time
from concurrent.futures import ThreadPoolExecutor
def process_slice(r, run_id):
    with open(r['input_path'], 'r', encoding='utf-8', errors='ignore') as f:
        f.seek(int(r['slice_start'])); content = f.read(int(r['slice_end']) - int(r['slice_start']))
    res = {"row_id": r['row_id'], "char_count": len(content), "line_count": content.count('\n')}
    os.makedirs(os.path.dirname(r['output_path']), exist_ok=True)
    with open(r['output_path'], 'w', encoding='utf-8') as f: json.dump(res, f)
    log_p = f"runs/{run_id}/lane_logs/lane{r['lane'].zfill(2)}.log"
    os.makedirs(os.path.dirname(log_p), exist_ok=True)
    with open(log_p, 'a') as l: l.write(f"{r['row_id']}\tDONE\n")
    return f"{run_id},{r['row_id']},{r['lane']},{r['semantic_dup_key']},0,{len(content)},10"

def main():
    run_id = sys.argv[1]
    with open(f"runs/{run_id}/work_packet.tsv", 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    with ThreadPoolExecutor(max_workers=8) as exe:
        res = list(exe.map(lambda r: process_slice(r, run_id), rows))
    with open(f"runs/{run_id}/receipt.jsonl", 'w', encoding='utf-8') as f: f.write("\n".join(res))
if __name__ == "__main__": main()
