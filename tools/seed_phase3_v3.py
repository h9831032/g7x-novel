import os
import json

def seed_catalog():
    # 파이참 프로젝트 루트 자동 인식
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(os.path.join(root, "engine"), exist_ok=True)
    os.makedirs(os.path.join(root, "GPTORDER"), exist_ok=True)

    tasks = {}
    # 버킷: A(120), B(60), C(36), D(24) = 총 240개
    buckets = [
        {"name": "CORE_WELD", "file": "main/manager.py", "count": 120},
        {"name": "FAILBOX_EVO", "file": "engine/failbox.py", "count": 60},
        {"name": "LLM_REAL", "file": "engine/basic_engine_v29.py", "count": 36},
        {"name": "DEVLOG_AUTO", "file": "tools/run_auto.py", "count": 24}
    ]

    current_idx = 0
    for b in buckets:
        for i in range(1, b["count"] + 1):
            current_idx += 1
            prefix = "box01_half1_seq" if current_idx <= 120 else "box01_half2_seq"
            seq_num = str((current_idx - 1) % 120 + 1).zfill(3)
            work_id = f"{prefix}{seq_num}"
            
            tasks[work_id] = {
                "work_id": work_id,
                "bucket": b["name"],
                "objective": f"PHASE 3: Concrete {b['name']} implementation for {work_id}. Patch {b['file']}.",
                "outputs": [b["file"]],
                "acceptance": f"File {b['file']} SHA1 change; 4h/23h report generated.",
                "task_type": b["name"]
            }

    with open(os.path.join(root, "engine", "work_catalog_v3.json"), "w", encoding="utf-8") as f:
        json.dump({"schema_version": 3, "tasks": tasks}, f, indent=4)

    ids = list(tasks.keys())
    with open(os.path.join(root, "GPTORDER", "REAL120_A.txt"), "w", encoding="utf-8") as f:
        for wid in ids[:120]: f.write(f"TASK_V2|payload={wid}\n")
    with open(os.path.join(root, "GPTORDER", "REAL120_B.txt"), "w") as f:
        for wid in ids[120:]: f.write(f"TASK_V2|payload={wid}\n")

    print(f"[OK] 240 Real Tasks Loaded in engine/work_catalog_v3.json")

if __name__ == "__main__":
    seed_catalog()