
import os
import json
import random

ROOT = r"C:\g7core\g7_v1"
BACKLOG_DIR = os.path.join(ROOT, "backlog", "cards")
os.makedirs(BACKLOG_DIR, exist_ok=True)

TASKS = [
    ("NOVEL", "Write a scene about a futuristic Seoul."),
    ("CODE", "Optimize a Python sorting algorithm."),
    ("LOGIC", "Analyze the fall of the Roman Empire."),
    ("TRANS", "Translate 'Hello World' to 5 languages.")
]

def generate_backlog():
    print(f">>> [SEED] Generating 600 tasks in {BACKLOG_DIR}...")
    for i in range(1, 601):
        t_type, t_prompt = TASKS[i % 4]
        card = {
            "card_id": f"CARD_{i:04d}",
            "priority": random.choice(["P0", "P1", "P2"]),
            "lane": f"LANE_{i%8}",
            "payload_type": t_type,
            "input_ref": f"internal_db_{i}",
            "prompt": f"{t_prompt} (Var_{i})",
            "created_at": "2026-01-06"
        }
        
        fname = os.path.join(BACKLOG_DIR, f"card_{i:04d}.json")
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(card, f, indent=4)
    
    print(">>> [SEED] 600 Cards Planted.")

if __name__ == "__main__":
    generate_backlog()
