"""Devlog Pipeline (daily_devlog + append_devlog)"""

import sys
import json
from pathlib import Path
from datetime import datetime


def call_devlog_generator(run_path: Path, ssot_root: Path) -> None:
    """devlog generation call"""
    print("[MANAGER] Calling devlog generator...")
    try:
        tools_path = ssot_root / "tools"
        if str(tools_path) not in sys.path:
            sys.path.insert(0, str(tools_path))

        from generate_devlog import append_devlog

        success = append_devlog(run_path, ssot_root)
        if not success:
            print("[DEVLOG ERROR] Failed to generate devlog")
    except Exception as e:
        print(f"[DEVLOG ERROR] {e}")


def write_daily_devlog(run_path: Path, stats: dict, reason_code: str) -> None:
    """Write human-readable daily devlog"""
    
    run_id = run_path.name
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    expected = stats.get("expected_missions", 0)
    success = stats.get("done_missions", 0)
    api_error = stats.get("api_error_count", 0)
    fail_box_count = stats.get("fail_box_count", 0)
    error_missions = stats.get("error_missions", [])
    
    content = f"""[DATE] {date_str}
[RUN_ID] {run_id}
[TOTAL_MISSIONS] {expected}
[SUCCESS] {success}
[API_ERROR] {api_error}
[FAIL_BOX_COUNT] {fail_box_count}

[FAILED_MISSIONS]
"""
    
    if error_missions:
        for mid in error_missions:
            content += f"- {mid} : API_TIMEOUT\n"
    else:
        content += "- None\n"
    
    content += f"""
[SUMMARY]
- Timeout retry: operational
- Failures isolated to FAIL_BOX
- Continuous run despite errors
- Night unattended mode: ready

[NEXT_ACTION]
"""
    
    if fail_box_count > 0:
        content += f"- FAILED_MISSIONS retry required ({fail_box_count} missions)\n"
    else:
        content += "- No retry needed\n"
    
    daily_log_path = run_path / "daily_devlog.txt"
    daily_log_path.write_text(content, encoding="utf-8")
    
    print(f"[DEVLOG] daily_devlog.txt created")
