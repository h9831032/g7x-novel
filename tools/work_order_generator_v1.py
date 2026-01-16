# C:\g7core\g7_v1\tools\work_order_generator_v1.py
import os, json, uuid, time
from datetime import datetime

ROOT = r"C:\g7core\g7_v1"
OUT_DIR = os.path.join(ROOT, "queue", "work_orders")
PROMPT_DIR = os.path.join(ROOT, "queue", "prompts")
STOP_FILE = os.path.join(ROOT, "queue", "STOP.txt")
os.makedirs(OUT_DIR, exist_ok=True)

def generate():
    print(">>> [ORDER_GEN] Mapping prompts to work orders...")
    prompts = [f for f in os.listdir(PROMPT_DIR) if f.endswith(".txt")]
    for i, p_file in enumerate(prompts):
        if os.path.exists(STOP_FILE): break
        o_id = str(uuid.uuid4())
        order = {
            "order_id": o_id,
            "lane": (i % 8) + 1,
            "task_type": "DEVLOG_TEST",
            "prompt_path": os.path.join(PROMPT_DIR, p_file),
            "meta": {"timestamp": datetime.now().isoformat()}
        }
        with open(os.path.join(OUT_DIR, f"ORD_{o_id}.json"), "w", encoding="utf-8") as f:
            json.dump(order, f)
        if i % 50 == 0: print(f"  Generated {i} orders...")

if __name__ == "__main__":
    generate()