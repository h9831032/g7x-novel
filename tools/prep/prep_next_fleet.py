import os, json

def prep_fleet(truck_ids):
    for t_id in truck_ids:
        root = f"C:\\g7core\\g7_v1\\runs\\REAL\\truck{t_id}"
        os.makedirs(root, exist_ok=True)
        
        for i in range(1, 21):
            bundle_dir = os.path.join(root, f"bundle_{i:02d}")
            os.makedirs(bundle_dir, exist_ok=True)
            
            packet_path = os.path.join(bundle_dir, "bundle_packet.jsonl")
            with open(packet_path, "w", encoding='utf-8') as f:
                for j in range(1, 7):
                    row_id = f"{t_id}_{((i-1)*6)+j:03d}"
                    task = {
                        "row_id": row_id,
                        "input_path": f"C:\\data\\source_{row_id}.txt",
                        "api_required": True
                    }
                    f.write(json.dumps(task) + "\n")
        print(f">>> [PREP] Truck {t_id} 120 Tasks Loaded.")

if __name__ == "__main__":
    prep_fleet(['D', 'E', 'F'])