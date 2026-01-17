#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G7X FAIL_BOX Packer v1

Checks the latest RUN folder for failures (exitcode != 0).
If failed:
  - Copies entire RUN folder to FAIL_BOX/
  - Appends entry to FAIL_BOX/FAIL_INDEX.jsonl

If successful: Does nothing.
"""
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

SSOT_ROOT = Path(r"C:\g7core\g7_v1")
RUNS_DIR = SSOT_ROOT / "runs"
FAIL_BOX_DIR = SSOT_ROOT / "FAIL_BOX"
FAIL_INDEX = FAIL_BOX_DIR / "FAIL_INDEX.jsonl"


def main():
    print("[FAIL_BOX_PACKER] Checking latest RUN for failures...")

    # 1. Check runs directory exists
    if not RUNS_DIR.exists():
        print("[INFO] runs directory not found. Nothing to pack.")
        return

    # 2. Find latest RUN folder
    run_folders = sorted([d for d in RUNS_DIR.iterdir() if d.is_dir() and d.name.startswith("RUN_")])

    if not run_folders:
        print("[INFO] No RUN folders found. Nothing to pack.")
        return

    latest_run = run_folders[-1]
    print(f"[INFO] Latest RUN: {latest_run.name}")

    # 3. Check exitcode.txt
    exitcode_file = latest_run / "exitcode.txt"
    if not exitcode_file.exists():
        print("[WARN] exitcode.txt not found. Cannot determine success/failure.")
        return

    with open(exitcode_file, encoding="utf-8") as f:
        exitcode = int(f.read().strip())

    print(f"[INFO] Exitcode: {exitcode}")

    # 4. If successful, skip
    if exitcode == 0:
        print("[SKIP] RUN successful (exitcode=0). No packing needed.")
        return

    # 5. RUN failed - pack to FAIL_BOX
    print(f"[FAIL] RUN failed (exitcode={exitcode}). Packing to FAIL_BOX...")

    # Create FAIL_BOX directory if not exists
    FAIL_BOX_DIR.mkdir(exist_ok=True)

    # Copy RUN folder to FAIL_BOX
    dest_path = FAIL_BOX_DIR / latest_run.name
    if dest_path.exists():
        print(f"[WARN] {dest_path.name} already exists in FAIL_BOX. Skipping copy.")
    else:
        shutil.copytree(latest_run, dest_path)
        print(f"[COPY] Copied to {dest_path}")

    # 6. Append to FAIL_INDEX.jsonl
    fail_entry = {
        "run_id": latest_run.name,
        "exitcode": exitcode,
        "packed_at": datetime.now().isoformat(),
        "source_path": str(latest_run),
        "fail_box_path": str(dest_path)
    }

    with open(FAIL_INDEX, "a", encoding="utf-8") as f:
        f.write(json.dumps(fail_entry, ensure_ascii=False) + "\n")

    print(f"[INDEX] Added to {FAIL_INDEX.name}")
    print("")
    print("[SUCCESS] Failed RUN packed to FAIL_BOX!")
    print(f"  Source: {latest_run}")
    print(f"  Destination: {dest_path}")


if __name__ == "__main__":
    main()
