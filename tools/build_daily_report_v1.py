#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G7X Daily Report Builder v1

Generates DEVLOG/DAILY_REPORT_YYYY-MM-DD.txt with:
- EVIDENCE: Latest RUN_PATH + PASS/FAIL status
- DELTA: Changed files (from git status or manual scan)
- INTEGRATION: One-line INTEGRATION_MAP summary
- NEXT: One-line next action
"""
import sys
import json
from pathlib import Path
from datetime import datetime

SSOT_ROOT = Path(r"C:\g7core\g7_v1")
RUNS_DIR = SSOT_ROOT / "runs"
DEVLOG_DIR = SSOT_ROOT / "DEVLOG"
INTEGRATION_MAP = DEVLOG_DIR / "INTEGRATION_MAP.md"


def main():
    print("[DAILY_REPORT] Generating daily report...")

    today = datetime.now().strftime("%Y-%m-%d")
    report_file = DEVLOG_DIR / f"DAILY_REPORT_{today}.txt"

    # Create DEVLOG directory if not exists
    DEVLOG_DIR.mkdir(exist_ok=True)

    # 1. EVIDENCE: Latest RUN status
    evidence_section = build_evidence_section()

    # 2. DELTA: Changed files (simplified - just note manual tracking)
    delta_section = build_delta_section()

    # 3. INTEGRATION: One-line summary
    integration_section = build_integration_section()

    # 4. NEXT: One-line next action
    next_section = "NEXT: Continue with next ORDER execution or run REAL missions."

    # Assemble report
    report_lines = [
        f"=== G7X DAILY REPORT - {today} ===",
        "",
        "## EVIDENCE",
        evidence_section,
        "",
        "## DELTA",
        delta_section,
        "",
        "## INTEGRATION",
        integration_section,
        "",
        "## NEXT",
        next_section,
        "",
        f"Generated at: {datetime.now().isoformat()}",
        ""
    ]

    # Write report
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"[SUCCESS] Daily report created: {report_file.name}")
    print(f"  Path: {report_file}")


def build_evidence_section() -> str:
    """Build EVIDENCE section with latest RUN status."""
    if not RUNS_DIR.exists():
        return "No RUN folders found."

    run_folders = sorted([d for d in RUNS_DIR.iterdir() if d.is_dir() and d.name.startswith("RUN_")])

    if not run_folders:
        return "No RUN folders found."

    latest_run = run_folders[-1]

    # Check exitcode
    exitcode_file = latest_run / "exitcode.txt"
    if exitcode_file.exists():
        with open(exitcode_file, encoding="utf-8") as f:
            exitcode = int(f.read().strip())
        status = "PASS" if exitcode == 0 else "FAIL"
    else:
        status = "UNKNOWN"

    # Check verify_report for mission count
    verify_file = latest_run / "verify_report.json"
    mission_info = ""
    if verify_file.exists():
        with open(verify_file, encoding="utf-8") as f:
            verify_data = json.load(f)
            done = verify_data.get("done_missions", 0)
            expected = verify_data.get("expected_missions", 0)
            mission_info = f" ({done}/{expected} missions)"

    return f"Latest RUN: {latest_run.name} - {status}{mission_info}\nPath: {latest_run}"


def build_delta_section() -> str:
    """Build DELTA section - simplified version."""
    return "Changed files tracked in git. Run 'git status' for details."


def build_integration_section() -> str:
    """Build INTEGRATION section from INTEGRATION_MAP.md."""
    if not INTEGRATION_MAP.exists():
        return "INTEGRATION_MAP.md not found."

    # Read first meaningful line from INTEGRATION_MAP
    with open(INTEGRATION_MAP, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                return f"Pipeline: {line}"

    return "Pipeline structure: manager.py → catalog → runner → evidence → devlog"


if __name__ == "__main__":
    main()
