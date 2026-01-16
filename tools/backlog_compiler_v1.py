import json, os, hashlib, sys

BASE_DIR = r"C:\g7core\g7_v1"

def compile_backlog(input_path):
    # 1. 원본 읽기
    real_tasks = []
    if os.path.exists(input_path):
        with open(input_path, 'r', encoding='utf-8') as f:
            real_tasks = [line.strip() for line in f if line.strip()]
    
    # 2. 240개 채우기 (A: 120, B: 120)
    total_needed = 240
    all_tasks = []
    for i in range(total_needed):
        if i < len(real_tasks):
            all_tasks.append({"payload": real_tasks[i], "real_work": True})
        else:
            # 더미 슬롯 (리팩토링/문서 등 기본 작업)
            all_tasks.append({"payload": "System Maintenance Task", "real_work": False})
            
    # 3. 패킷 분할 및 시그니처 생성
    for t_id, start_idx in [("A", 0), ("B", 120)]:
        packet_path = os.path.join(BASE_DIR, f"packet_{t_id}.jsonl")
        chunk = all_tasks[start_idx:start_idx+120]
        
        with open(packet_path, 'w', encoding='utf-8', newline='\n') as f:
            for idx, item in enumerate(chunk):
                sig_raw = f"{t_id}::{idx:03d}::{item['payload']}"
                sig = hashlib.sha256(sig_raw.encode()).hexdigest()[:16]
                row = {
                    "row_id": idx + 1,
                    "task_signature": f"{t_id}::{sig}",
                    "payload": item["payload"],
                    "real_work": item["real_work"]
                }
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"### [COMPILER] {t_id} Packet ready (120 lines).")

if __name__ == "__main__":
    if len(sys.argv) > 1: compile_backlog(sys.argv[1])