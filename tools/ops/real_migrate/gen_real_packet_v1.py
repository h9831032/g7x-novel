import os, sys, csv, math
def gen():
    input_dir = r"C:\g6core\g6_v24\data\umr\chunks"
    files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    count = len(files)
    if count == 0: print("FATAL: No files to migrate"); sys.exit(2)
    
    half = count // 2
    trucks = {'A': files[:half], 'B': files[half:]}
    
    for name in ['A', 'B']:
        subset = trucks[name]
        run_id = sys.argv[1] if name == 'A' else sys.argv[2]
        os.makedirs(f"runs/{run_id}", exist_ok=True)
        if not subset: continue
        
        path = f"runs/{run_id}/work_packet.tsv"
        lane_size = math.ceil(len(subset) / 8) if len(subset) >= 8 else 1
        
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=["row_id","lane","kind","input_path","output_path","filename"], delimiter='\t')
            w.writeheader()
            for i, fn in enumerate(subset):
                lane = (i // lane_size) + 1
                if lane > 8: lane = 8
                w.writerow({"row_id": i+1, "lane": lane, "kind": "DATA", "input_path": os.path.join(input_dir, fn),
                            "output_path": f"C:/g7core/g7_v1/data_output/ready/{name}/{fn}", "filename": fn})
    print(f"SUCCESS: Split {count} files between A and B.")
if __name__ == "__main__": gen()
