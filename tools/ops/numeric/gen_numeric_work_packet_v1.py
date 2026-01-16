import os, sys, csv
def gen():
    truck, run_id = sys.argv[1], sys.argv[2]
    run_dir = f"runs/{run_id}"
    input_dir = f"{run_dir}/inputs"
    os.makedirs(input_dir, exist_ok=True)
    start_n = 1 if truck == 'A' else 121
    rows = []
    for i in range(120):
        n = start_n + i
        row_id, lane = i + 1, (i // 15) + 1
        in_path = f"{input_dir}/num_{str(row_id).zfill(3)}.txt"
        with open(in_path, 'w') as f: f.write(str(n))
        rows.append({"row_id": row_id, "lane": lane, "kind": "DATA", "n": n, "input_path": in_path, "output_path": f"{run_dir}/payload/row_{str(row_id).zfill(3)}.json"})
    with open(f"{run_dir}/work_packet.tsv", 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=["row_id","lane","kind","n","input_path","output_path"], delimiter='\t')
        w.writeheader(); w.writerows(rows)
if __name__ == "__main__": gen()
