import json
import os
import hashlib

class PacketGenerator:
    def __init__(self, ssot_root, input_chunks):
        self.root = ssot_root
        self.input_chunks = input_chunks
        self.bundle_size = 6
        self.rows_per_truck = 120

    def generate(self, truck_id, run_id):
        truck_dir = os.path.join(self.root, "runs", run_id, f"truck{truck_id}")
        os.makedirs(truck_dir, exist_ok=True)
        all_tasks = []
        for i in range(1, self.rows_per_truck + 1):
            task = {
                "row_id": f"{truck_id}_{i:03d}",
                "input_path": os.path.join(self.input_chunks, f"chunk_{i:03d}.txt"),
                "action": "LAW60_VERIFY",
                "api_required": (i % 6 == 1)
            }
            all_tasks.append(task)

        for b_idx in range(20):
            bundle_tasks = all_tasks[b_idx*6 : (b_idx+1)*6]
            bundle_path = os.path.join(truck_dir, f"bundle_{b_idx+1:02d}")
            os.makedirs(bundle_path, exist_ok=True)
            with open(os.path.join(bundle_path, "bundle_packet.jsonl"), "w", encoding="utf-8") as f:
                for t in bundle_tasks:
                    f.write(json.dumps(t, ensure_ascii=False) + "\n")
        print(f">>> [PACKET] Truck {truck_id}: 20 Bundles Generated in runs/{run_id}")

if __name__ == "__main__":
    # 경로 동기화: REAL_BATTLE_FINAL 대신 REAL로 생성
    gen = PacketGenerator(r"C:\g7core\g7_v1", r"C:\g6core\g6_v24\data\umr\chunks")
    gen.generate("A", "REAL")
    gen.generate("B", "REAL")