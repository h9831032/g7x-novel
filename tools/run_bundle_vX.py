import os
import sys
import json
import hashlib
from datetime import datetime

# [T001] 표준 경로 봉인
SSOT_ROOT = r"C:\g7core\g7_v1"
RUNS_ROOT = os.path.join(SSOT_ROOT, "runs", "REAL")
RECEIPT_PATH = os.path.join(RUNS_ROOT, "api_receipt.jsonl")
BUDGET_LOG_PATH = os.path.join(RUNS_ROOT, "budget_guard.log")

def update_budget_guard():
    """[M1] 영수증에서 가계부 자동 추출 및 갱신"""
    if not os.path.exists(RECEIPT_PATH): return
    
    total_calls = 0
    with open(RECEIPT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip(): total_calls += 1
            
    with open(BUDGET_LOG_PATH, "w", encoding="utf-8") as f:
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "calls_total": total_calls,
            "status": "ACTIVE"
        }
        f.write(json.dumps(log_data))

def finalize_micro_bundle(truck_id, bundle_id, tasks_res):
    """[M2, M5] 3개 단위 증거팩 및 일지 자동 생성"""
    truck_path = os.path.join(RUNS_ROOT, truck_id, "FINAL")
    os.makedirs(truck_path, exist_ok=True)
    
    # DEVLOG 기록
    devlog_path = os.path.join(RUNS_ROOT, "DEVLOG", "devlog.jsonl")
    os.makedirs(os.path.dirname(devlog_path), exist_ok=True)
    with open(devlog_path, "a", encoding="utf-8") as f:
        log_entry = {"ts": datetime.now().isoformat(), "truck": truck_id, "bundle": bundle_id, "count": len(tasks_res)}
        f.write(json.dumps(log_entry) + "\n")
        
    update_budget_guard()

if __name__ == "__main__":
    # 실행부 로직 (생략: 3+3 분할 루프 포함)
    print(">>> INTEGRATED RUNNER V_X LOADED.")
    # 임시 실행 확인용
    update_budget_guard()
    print(f">>> BudgetGuard updated at: {BUDGET_LOG_PATH}")