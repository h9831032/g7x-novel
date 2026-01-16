"""Retry Order Generator from FAIL_BOX"""

import json
from pathlib import Path
from datetime import datetime


def generate_retry_order(run_path: Path, ssot_root: Path, original_order_path: Path) -> None:
    """Generate retry order file from FAIL_BOX events"""
    
    fail_events_file = run_path / "FAIL_BOX" / "events" / "fail_events.jsonl"
    
    if not fail_events_file.exists():
        print("[RETRY_ORDER] No fail_events.jsonl - skip retry order generation")
        return
    
    failed_missions = []
    
    with open(fail_events_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                mission_id = event.get("mission_id", "")
                order_prefix = event.get("order_prefix", "")
                if mission_id and order_prefix:
                    failed_missions.append((mission_id, order_prefix))
            except Exception:
                continue
    
    if not failed_missions:
        print("[RETRY_ORDER] No failed missions - skip retry order generation")
        return
    
    original_orders = {}
    if original_order_path.exists():
        with open(original_order_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    original_orders[f"mission_{idx:04d}"] = line
    
    date_str = datetime.now().strftime("%Y%m%d")
    run_id_short = run_path.name.split("_")[1] if "_" in run_path.name else "UNKNOWN"
    retry_filename = f"RETRY_WORK_{date_str}_{run_id_short}.txt"
    retry_path = ssot_root / "GPTORDER" / retry_filename
    
    with open(retry_path, "w", encoding="utf-8") as f:
        for mission_id, order_prefix in failed_missions:
            original_order = original_orders.get(mission_id, order_prefix)
            f.write(original_order + "\n")
    
    print(f"[RETRY_ORDER] Generated: {retry_filename} ({len(failed_missions)} missions)")
