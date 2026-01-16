import os
import json
import random

ROOT = r"C:\g7core\g7_v1"
QUEUE_DIR = os.path.join(ROOT, "queue", "work_orders")
os.makedirs(QUEUE_DIR, exist_ok=True)

# ---------------------------------------------------------
# [1] Main Engine Upgrade (Hardcoding Removed)
# ---------------------------------------------------------
main_v2_code = r'''
import os
import json
import time
import sys
import datetime
from tools.devlog_manager import DevLogManager
from tools.real_runner import RealRunner

ROOT = r"C:\g7core\g7_v1"
QUEUE_DIR = os.path.join(ROOT, "queue", "work_orders")
RECEIPT_FILE = os.path.join(ROOT, "runs", "REAL", "api_receipt.jsonl")
CONFIG_FILE = os.path.join(ROOT, "config", "secrets.json")

def load_api_key():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("gemini_api_key")

def main():
    brain = DevLogManager(ROOT)
    run_id = f"RUN_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    brain.log_event(run_id, "INIT", "PHASE-5_START")

    api_key = load_api_key()
    if not api_key:
        print("!!! No API Key.")
        return
    engine = RealRunner(api_key)

    # 대기열 스캔 (JSON 파일만)
    work_files = [f for f in os.listdir(QUEUE_DIR) if f.endswith(".json")]
    print(f">>> [RUNNING] {run_id} | Found {len(work_files)} tasks in queue.")

    if not work_files:
        print(">>> [IDLE] Queue empty.")
        return

    # [PHASE-5] Bulk Execution Loop
    success_count = 0
    for i, filename in enumerate(work_files):
        file_path = os.path.join(QUEUE_DIR, filename)
        
        # [FIX] 파일 내용을 실제로 읽음 (하드코딩 제거)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                task_data = json.load(f)
                prompt = task_data.get("prompt", "NO_PROMPT")
                task_id = task_data.get("task_id", filename)
        except Exception as e:
            print(f"   [SKIP] Read Error: {filename}")
            continue

        print(f"   [{i+1}/{len(work_files)}] Processing {task_id}...", end="\r")
        
        # 실제 API 호출
        success, output, receipt = engine.execute_task(prompt)
        
        if success:
            receipt['task_id'] = task_id
            with open(RECEIPT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(receipt, ensure_ascii=False) + "\n")
            success_count += 1
            
            # [Cleanup] 완료된 일감은 삭제 (재처리 방지)
            os.remove(file_path) 
        else:
            brain.log_event(run_id, "EXEC", "FAIL", {"file": filename, "error": output})

    brain.log_event(run_id, "SUMMARY", "DONE", {"processed": success_count})
    print(f"\n>>> [DONE] {success_count} tasks completed. Receipt updated.")

if __name__ == "__main__":
    main()
'''
with open(os.path.join(ROOT, "main.py"), "w", encoding="utf-8") as f:
    f.write(main_v2_code)

# ---------------------------------------------------------
# [2] Mass Load Generator (120 Real Tasks)
# ---------------------------------------------------------
print(">>> [GENERATING] Creating 120 diverse work orders...")

prompts = [
    ("NOVEL", "Write a gloomy opening sentence for a cyberpunk novel."),
    ("CODE", "Write a Python function to calculate Fibonacci numbers."),
    ("LOGIC", "Explain why the sky is blue in one sentence."),
    ("DATA", "Convert 'Name: John, Age: 30' into JSON format.")
]

for i in range(1, 121): # 120개 생성
    category, text = prompts[i % 4]
    order = {
        "task_id": f"TASK_{i:03d}_{category}",
        "type": category,
        "prompt": f"{text} (Variation {i})"
    }
    with open(os.path.join(QUEUE_DIR, f"order_{i:03d}.json"), "w", encoding="utf-8") as f:
        json.dump(order, f, indent=4)

print(f">>> [DEPLOY] PHASE-5 Ready. 120 Tasks loaded in {QUEUE_DIR}")