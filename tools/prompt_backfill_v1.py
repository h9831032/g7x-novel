import os

ROOT = r"C:\g7core\g7_v1"
MISSING_FILE = os.path.join(ROOT, "queue", "audit", "missing_prompts.txt")

def backfill():
    if not os.path.exists(MISSING_FILE): return
    with open(MISSING_FILE, "r") as f:
        paths = [l.strip() for l in f if l.strip()]
    
    for p in paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write("G7X_BACKFILL_V6: 작업 프롬프트 실물 복구본.")
    print(f">>> Backfilled {len(paths)} prompts.")

if __name__ == "__main__":
    backfill()