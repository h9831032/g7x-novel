import os
import json
import uuid
import random
import datetime
import sys

# CONFIGURATION
ROOT = r"C:\g7core\g7_v1"
STOP_FILE = os.path.join(ROOT, "STOP.txt")
QUEUE_BASE = os.path.join(ROOT, "queue", "work_orders")

def generate_batch():
    # 1. FAIL FAST CHECK
    if os.path.exists(STOP_FILE):
        # STOP signal detected, exit silently or with code 0 as it's a control logic
        sys.exit(0)

    # 2. PREPARE DIRECTORY
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    target_dir = os.path.join(QUEUE_BASE, today_str)
    
    try:
        os.makedirs(target_dir, exist_ok=True)
    except Exception:
        sys.exit(1)

    # 3. DEFINE BATCH META
    batch_suffix = datetime.datetime.now().strftime("%H%M%S") + "_" + str(uuid.uuid4())[:4]
    filename = f"batch_{batch_suffix}.jsonl"
    filepath = os.path.join(target_dir, filename)

    task_types = [
        "DEVLOG_TEST", 
        "NOVEL_CHUNK_ANALYZE", 
        "BLUEPRINT_EXTRACT", 
        "STYLE_CARTRIDGE_APPLY", 
        "GUARDIAN_CHECK", 
        "INDEX_TAGGING"
    ]

    # 4. GENERATE 30 ORDERS
    orders = []
    for _ in range(30):
        order = {
            "order_id": str(uuid.uuid4()),
            "lane": random.randint(1, 8),
            "task_type": random.choice(task_types),
            "prompt_path": "ABS_PATH",
            "meta": {
                "created_at": datetime.datetime.now().isoformat()
            }
        }
        orders.append(order)

    # 5. PHYSICAL WRITE (JSONL)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            for o in orders:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
    except Exception:
        sys.exit(1)

    # 6. PROOF OUTPUT (Required Format)
    print(filepath)
    print(orders[0]["order_id"])

if __name__ == "__main__":
    generate_batch()