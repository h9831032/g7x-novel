import os, json
from datetime import datetime

def seed_devlog_orders():
    root = r"C:\g7core\g7_v1"
    os.makedirs(os.path.join(root, "engine"), exist_ok=True)
    os.makedirs(os.path.join(root, "GPTORDER"), exist_ok=True)

    # 1. Catalog 생성 (120개 Task 정의)
    tasks = {}
    for i in range(1, 121):
        work_id = f"devlog_tick_{i:03d}"
        tasks[work_id] = {
            "id": work_id,
            "objective": f"tick {i:03d}: simclock +2min, scheduler.check(4h/23:00) and log activity.",
            "outputs": [f"runs/REAL/DEVLOG/tick_{i:03d}.log"],
            "acceptance": "Devlog scheduler must evaluate time and generate files if conditions met."
        }
    
    with open(os.path.join(root, "engine", "work_catalog_phase3_devlog_v1.json"), "w", encoding="utf-8") as f:
        json.dump({"schema_version": 3, "tasks": tasks}, f, indent=4)

    # 2. Order File 생성 (META 포함)
    order_path = os.path.join(root, "GPTORDER", "REAL120_DEVLOG_A.txt")
    with open(order_path, "w", encoding="utf-8") as f:
        f.write("META|start=2026-01-10T19:10:00|step_min=2|mode=SIMCLOCK\n")
        for i in range(1, 121):
            f.write(f"TASK_V2|payload=devlog_tick_{i:03d}\n")

    print(f"[CREATED] {os.path.join(root, 'engine', 'work_catalog_phase3_devlog_v1.json')}")
    print(f"[CREATED] {order_path}")

if __name__ == "__main__":
    seed_devlog_orders()