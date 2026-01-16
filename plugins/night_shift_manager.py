# C:\g7core\g7_v1\plugins\night_shift_manager.py
import datetime
import json
import os

def record_api_receipt(run_dir, data):
    """
    지시서 규격 필드: ts, run_id, order_id, task_type, payload_raw, model, status, error
    """
    receipt_path = os.path.join(run_dir, "api_receipt.jsonl")
    
    # [WELDING] resp/response 오타 수정 및 데이터 매핑
    receipt_entry = {
        "ts": datetime.datetime.now().isoformat(),
        "run_id": data.get("run_id"),
        "order_id": data.get("order_id"),
        "task_type": data.get("task_type", "UNKNOWN"),
        "payload_raw": data.get("payload", ""),
        "model": data.get("model", "gemini-2.0-flash"),
        "status": data.get("status", "SUCCESS"),
        "error": data.get("error", "")
    }
    
    with open(receipt_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(receipt_entry, ensure_ascii=False) + "\n")

def generate_stamp(run_dir, order_id, content):
    stamps_dir = os.path.join(run_dir, "stamps")
    os.makedirs(stamps_dir, exist_ok=True)
    stamp_path = os.path.join(stamps_dir, f"{order_id}.txt")
    with open(stamp_path, "w", encoding="utf-8") as f:
        f.write(content)
    return stamp_path