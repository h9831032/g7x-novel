import json, os, hashlib, sys

# [V33.6] 창 열림 방지 및 경로 강제 고정
BASE_DIR = r"C:\g7core\g7_v1"

def create_force():
    if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)
    for t_id in ["A", "B"]:
        path = os.path.join(BASE_DIR, f"packet_{t_id}.jsonl")
        data = []
        for i in range(1, 121):
            payload = f"Real Data Truck {t_id} Chunk #{i:03d}"
            sig = f"{t_id}::{hashlib.sha256(payload.encode()).hexdigest()[:12]}"
            data.append({"row_id": i, "task_signature": sig, "payload": payload})
        with open(path, "w", encoding="utf-8", newline='\n') as f:
            for item in data: f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"### [SUCCESS] Created: {path}")

if __name__ == "__main__":
    create_force()
    print(">>> [FINAL] All packets are deployed.")