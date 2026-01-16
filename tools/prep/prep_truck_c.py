import os, json

def prep_truck_c():
    root = "C:\\g7core\\g7_v1\\runs\\REAL\\truckC"
    os.makedirs(root, exist_ok=True)
    
    # 120발의 가짜/실제 데이터 시뮬레이션 (형님의 실제 원고가 있다면 여기서 로드)
    for i in range(1, 21):
        bundle_dir = os.path.join(root, f"bundle_{i:02d}")
        os.makedirs(bundle_dir, exist_ok=True)
        
        packet_path = os.path.join(bundle_dir, "bundle_packet.jsonl")
        with open(packet_path, "w", encoding='utf-8') as f:
            for j in range(1, 7):
                row_id = f"C_{((i-1)*6)+j:03d}"
                task = {
                    "row_id": row_id,
                    "input_path": f"C:\\data\\source_{row_id}.txt",
                    "api_required": True
                }
                f.write(json.dumps(task) + "\n")
    print(">>> [PREP] Truck C 120 Tasks Loaded (20 Bundles).")

if __name__ == "__main__":
    prep_truck_c()