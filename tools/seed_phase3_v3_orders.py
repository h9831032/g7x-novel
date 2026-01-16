import os
import json
from datetime import datetime

def seed_phase3_v3():
    root = r"C:\g7core\g7_v1"
    os.makedirs(os.path.join(root, "engine"), exist_ok=True)
    os.makedirs(os.path.join(root, "GPTORDER"), exist_ok=True)

    tasks = {}
    
    # [BUCKET A] Core Integration (120개) - 매니저 및 베이직 엔진 용접 [cite: 20, 118]
    for i in range(1, 121):
        work_id = f"box01_half1_seq{i:03d}"
        tasks[work_id] = {
            "id": work_id,
            "bucket": "INTEGRATION_WELD_CORE",
            "objective": f"Enforce strict validation for {work_id} in main/manager.py. Must record SHA1 and line count.",
            "outputs": ["main/manager.py"],
            "acceptance": "SHA1 of main/manager.py must change; Line count >= 200."
        }

    # [BUCKET B] FailBox & Requeue (60개) - 격리 및 복구 로직 
    for i in range(1, 61):
        work_id = f"box01_half2_seq{i:03d}"
        tasks[work_id] = {
            "id": work_id,
            "bucket": "FAILBOX_REQUEUE_PROOF",
            "objective": f"Update engine/failbox.py to handle state transition for {work_id}. Ensure isolation triggers.",
            "outputs": ["engine/failbox.py"],
            "acceptance": "fail_reason.json must be generated in FAIL_BOX directory."
        }

    # [BUCKET C] LLM Real (40개) - 어댑터 및 API 접합 
    for i in range(61, 101):
        work_id = f"box01_half2_seq{i:03d}"
        tasks[work_id] = {
            "id": work_id,
            "bucket": "LLM_REAL_CONNECTION",
            "objective": f"Integrate REAL LLM Adapter in basic_engine_v29.py for task {work_id}. (Mock removal phase).",
            "outputs": ["engine/basic_engine_v29.py"],
            "acceptance": "api_receipt.jsonl must contain non-zero usage tokens."
        }

    # [BUCKET D] DevLog & Report (20개) - 자동화 일지 
    for i in range(101, 121):
        work_id = f"box01_half2_seq{i:03d}"
        tasks[work_id] = {
            "id": work_id,
            "bucket": "DEVLOG_AUTO_DAILY",
            "objective": f"Implement 4h snapshot and 23:00 daily report logic for {work_id} in tools/run_auto.py.",
            "outputs": ["tools/run_auto.py"],
            "acceptance": "daily_report_YYYYMMDD.md must exist in runs/REAL/REPORT/."
        }

    # Save Catalog V3
    catalog_path = os.path.join(root, "engine", "work_catalog_v3.json")
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"schema_version": 3, "tasks": tasks}, f, indent=4, ensure_ascii=False)

    # Generate Order Files (A/B) 
    with open(os.path.join(root, "GPTORDER", "REAL120_A.txt"), "w") as f:
        for i in range(1, 121): f.write(f"TASK_V2|payload=box01_half1_seq{i:03d}\n")
    
    with open(os.path.join(root, "GPTORDER", "REAL120_B.txt"), "w") as f:
        for i in range(1, 121): f.write(f"TASK_V2|payload=box01_half2_seq{i:03d}\n")

    print("[OK] Phase 3: Work Catalog V3 (240 Real Tasks) & Orders Initialized.")

if __name__ == "__main__":
    seed_phase3_v3()