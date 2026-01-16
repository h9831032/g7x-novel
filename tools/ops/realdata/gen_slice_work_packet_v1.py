import os, sys, csv
def gen():
    input_dir = r"C:\g6core\g6_v24\data\umr\chunks"
    files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))][:12]
    if len(files) < 12: sys.exit(2)
    
    for truck in ['A', 'B']:
        run_id = sys.argv[1] if truck == 'A' else sys.argv[2]
        os.makedirs(f"runs/{run_id}", exist_ok=True)
        rows = []
        for f_idx, fn in enumerate(files):
            fpath = os.path.join(input_dir, fn)
            fsize = os.path.getsize(fpath)
            slice_size = fsize // 20
            indices = range(1, 21, 2) if truck == 'A' else range(2, 21, 2)
            for s_idx in indices:
                start = (s_idx - 1) * slice_size
                end = start + slice_size if s_idx < 20 else fsize
                row_id = len(rows) + 1
                rows.append({
                    "row_id": row_id, "lane": str(((row_id-1)//15)+1),
                    "input_path": fpath, "slice_start": start, "slice_end": end,
                    "output_path": f"C:/g7core/g7_v1/runs/{run_id}/payload/row_{row_id:03d}.json",
                    "task_signature": f"SLICE_{truck}_{f_idx}_{s_idx}",
                    "semantic_dup_key": f"SLICE|{fpath}|{start}|{end}"
                })
        with open(f"runs/{run_id}/work_packet.tsv", 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter='\t')
            w.writeheader(); w.writerows(rows)
if __name__ == "__main__": gen()
