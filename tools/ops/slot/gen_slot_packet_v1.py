import os, sys, csv
def get_slot(i):
    if i < 60: return 'A'
    if i < 96: return 'B'
    if i < 114: return 'C'
    return 'D'
def gen():
    truck, run_id = sys.argv[1], sys.argv[2]
    run_dir = f"runs/{run_id}"
    os.makedirs(f"{run_dir}/inputs", exist_ok=True)
    input_dir = r"C:\g6core\g6_v24\data\umr\chunks"
    files = sorted([f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))])
    rows = []
    seen_keys = set()
    for i in range(120):
        slot_type = get_slot(i)
        if slot_type == 'D': slot_type = 'A'
        row_id, lane = i + 1, (i // 15) + 1
        offset = 0 if truck == 'A' else 120
        file_idx = (i + offset) % len(files)
        target_file = files[file_idx]
        dup_key = f"SLOT_{slot_type}|{target_file}|SLICE_{i+offset}"
        if dup_key in seen_keys: sys.exit(2)
        seen_keys.add(dup_key)
        rows.append({"row_id": row_id, "lane": lane, "slot": slot_type, "semantic_dup_key": dup_key,
                    "input_path": os.path.join(input_dir, target_file),
                    "output_path": f"{run_dir}/payload/row_{str(row_id).zfill(3)}.json"})
    with open(f"{run_dir}/work_packet.tsv", 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter='\t')
        w.writeheader(); w.writerows(rows)
if __name__ == "__main__": gen()
