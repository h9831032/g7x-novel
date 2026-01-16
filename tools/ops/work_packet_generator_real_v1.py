import os, sys, csv, math
def gen():
    input_dir = r"C:\g6core\g6_v24\data\umr\chunks"
    files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    count = len(files)
    if count == 0:
        print("FATAL: No files found in input directory."); sys.exit(2)
    
    # 240개가 안되면 현재 개수를 반으로 나눔
    half = count // 2
    trucks = {'A': files[:half], 'B': files[half:]}
    
    for name, subset in trucks.items():
        if not subset: continue
        path = f"C:/g7core/g7_v1/tools/ops/work_packet_{name}.tsv"
        lane_size = math.ceil(len(subset) / 8) if len(subset) >= 8 else 1
        
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=["row_id","lane","kind","task_signature","semantic_dup_key","input_path","output_path","action"], delimiter='\t')
            w.writeheader()
            for i, fn in enumerate(subset):
                lane = (i // lane_size) + 1 if lane_size > 0 else 1
                if lane > 8: lane = 8
                w.writerow({
                    "row_id": i+1, "lane": str(lane), "kind": "DATA",
                    "task_signature": f"SIG_{fn}", "semantic_dup_key": f"DATA|{fn}|SYNC",
                    "input_path": os.path.join(input_dir, fn),
                    "output_path": f"C:/g7core/g7_v1/data_output/{name}/{fn}", "action": "SYNC"
                })
    print(f"SUCCESS: Packets generated for {count} files.")
if __name__ == "__main__": gen()
