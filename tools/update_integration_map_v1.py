#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G7X Integration Map Updater v1

Updates DEVLOG/INTEGRATION_MAP.md with:
- Files modified today
- Latest RUN_PATH
"""
import sys
from pathlib import Path
from datetime import datetime, date

SSOT_ROOT = Path(r"C:\g7core\g7_v1")
DEVLOG_DIR = SSOT_ROOT / "DEVLOG"
INTEGRATION_MAP = DEVLOG_DIR / "INTEGRATION_MAP.md"
RUNS_DIR = SSOT_ROOT / "runs"


def main():
    print("[UPDATE_INTEGRATION_MAP] Updating INTEGRATION_MAP.md...")

    # Read existing map
    if not INTEGRATION_MAP.exists():
        print("[WARN] INTEGRATION_MAP.md not found. Creating new.")
        content_lines = ["# G7X Integration Map\n", "\n"]
    else:
        with open(INTEGRATION_MAP, encoding="utf-8") as f:
            content_lines = f.readlines()

    # Find files modified today
    today = date.today()
    modified_today = []

    for folder in ["main", "tools", "GPTORDER", "DOCS", "DEVLOG"]:
        folder_path = SSOT_ROOT / folder
        if folder_path.exists():
            for file in folder_path.rglob("*"):
                if file.is_file():
                    mtime = datetime.fromtimestamp(file.stat().st_mtime).date()
                    if mtime == today:
                        rel_path = file.relative_to(SSOT_ROOT)
                        modified_today.append(str(rel_path))

    # Get latest RUN
    latest_run = "No RUN folders found"
    if RUNS_DIR.exists():
        run_folders = sorted([d for d in RUNS_DIR.iterdir() if d.is_dir() and d.name.startswith("RUN_")])
        if run_folders:
            latest_run = str(run_folders[-1])

    # Append update section
    update_section = [
        "\n",
        f"## Update - {datetime.now().isoformat()}\n",
        "\n",
        f"### Files Modified Today ({today}):\n"
    ]

    if modified_today:
        for file in sorted(modified_today)[:20]:  # Limit to 20 files
            update_section.append(f"- {file}\n")
    else:
        update_section.append("- (No files modified today)\n")

    update_section.append(f"\n### Latest RUN:\n")
    update_section.append(f"- {latest_run}\n")

    # Write updated map
    with open(INTEGRATION_MAP, "w", encoding="utf-8") as f:
        f.writelines(content_lines)
        f.writelines(update_section)

    print(f"[SUCCESS] INTEGRATION_MAP.md updated!")
    print(f"  Modified files today: {len(modified_today)}")
    print(f"  Latest RUN: {latest_run}")


if __name__ == "__main__":
    main()
