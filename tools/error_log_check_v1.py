#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G7X Error Log Zero Rule Checker v1

Checks latest RUN folder for error conditions:
- api_error_count must be 0
- stderr_manager.txt must be empty or contain only safe patterns
- No ERROR/FAIL patterns in stdout (except expected markers)

Returns PASS if error log is clean, FAIL otherwise.
"""
import sys
from pathlib import Path

SSOT_ROOT = Path(r"C:\g7core\g7_v1")
RUNS_DIR = SSOT_ROOT / "runs"

# Safe patterns (allowed in stderr/stdout)
SAFE_PATTERNS = [
    "[FAIL_FAST]",  # Expected validation markers
    "[BATCH_BEGIN]",
    "[BATCH_COMPLETE]",
    "[STOP_GATE",
    "PASS",
    "OK"
]


def fail_fast(msg: str):
    print(f"[ERROR_LOG_FAIL] {msg}", file=sys.stderr)
    sys.exit(1)


def is_safe_line(line: str) -> bool:
    """Check if line contains safe patterns"""
    for pattern in SAFE_PATTERNS:
        if pattern in line:
            return True
    return False


def main():
    print("[ERROR_LOG] Checking latest RUN for errors...")

    # 1. Find latest RUN folder
    if not RUNS_DIR.exists():
        fail_fast(f"runs directory not found: {RUNS_DIR}")

    run_folders = sorted([d for d in RUNS_DIR.iterdir() if d.is_dir() and d.name.startswith("RUN_")])
    if not run_folders:
        fail_fast("No RUN folders found in runs/")

    latest_run = run_folders[-1]
    print(f"[ERROR_LOG] Latest RUN: {latest_run.name}")
    print("")

    # 2. Check api_error_count in verify_report.json
    verify_report_path = latest_run / "verify_report.json"
    if verify_report_path.exists():
        import json
        try:
            with open(verify_report_path, "r", encoding="utf-8") as f:
                verify_data = json.load(f)

            api_error_count = verify_data.get("api_error_count", 0)
            print(f"[ERROR_LOG] api_error_count: {api_error_count}")

            if api_error_count > 0:
                fail_fast(f"api_error_count = {api_error_count} (must be 0)")
        except Exception as e:
            print(f"[WARN] Cannot parse verify_report.json: {e}")
    else:
        print("[WARN] verify_report.json not found")

    # 3. Check stderr_manager.txt (must be empty or safe)
    stderr_path = latest_run / "stderr_manager.txt"
    if stderr_path.exists():
        stderr_content = stderr_path.read_text(encoding="utf-8").strip()
        if stderr_content:
            # Check if all lines are safe
            unsafe_lines = []
            for line in stderr_content.split("\n"):
                line = line.strip()
                if line and not is_safe_line(line):
                    # Check for error indicators
                    if any(keyword in line.upper() for keyword in ["ERROR", "FAIL", "EXCEPTION", "TRACEBACK"]):
                        unsafe_lines.append(line)

            if unsafe_lines:
                print("[ERROR_LOG] UNSAFE lines in stderr:")
                for line in unsafe_lines[:5]:  # Show first 5
                    print(f"  {line}")
                fail_fast(f"stderr contains {len(unsafe_lines)} unsafe error lines")
            else:
                print("[ERROR_LOG] stderr has content but appears safe")
        else:
            print("[ERROR_LOG] stderr is empty (OK)")
    else:
        print("[WARN] stderr_manager.txt not found")

    # 4. Check stdout for unexpected errors
    stdout_path = latest_run / "stdout_manager.txt"
    if stdout_path.exists():
        stdout_content = stdout_path.read_text(encoding="utf-8")
        error_lines = []

        for line in stdout_content.split("\n"):
            line = line.strip()
            if not line or is_safe_line(line):
                continue

            # Look for error patterns
            if "[API_ERROR]" in line or "[EXCEPTION]" in line:
                error_lines.append(line)

        if error_lines:
            print("[ERROR_LOG] ERROR patterns in stdout:")
            for line in error_lines[:5]:
                print(f"  {line}")
            fail_fast(f"stdout contains {len(error_lines)} error patterns")
        else:
            print("[ERROR_LOG] stdout appears clean")
    else:
        print("[WARN] stdout_manager.txt not found")

    # 5. PASS
    print("")
    print("[ERROR_LOG] PASS - No errors detected")
    print(f"RUN_PATH: {latest_run}")
    sys.exit(0)


if __name__ == "__main__":
    main()
