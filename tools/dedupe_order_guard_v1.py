#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G7X GPTORDER Deduplication Guard v1

Scans GPTORDER/*.txt files and checks for:
- Duplicate SSOT_ORDER_ID values
- Missing SSOT_ORDER_ID
- Empty files (0 bytes)

Reports FAIL if any issues found.
"""
import sys
import re
from pathlib import Path
from typing import Dict, List

SSOT_ROOT = Path(r"C:\g7core\g7_v1")
GPTORDER_DIR = SSOT_ROOT / "GPTORDER"


def main():
    print("[DEDUPE_ORDER_GUARD] Checking GPTORDER files...")

    if not GPTORDER_DIR.exists():
        print("[FAIL] GPTORDER directory not found.")
        sys.exit(1)

    # Find all .txt files
    order_files = list(GPTORDER_DIR.glob("*.txt"))
    print(f"[INFO] Found {len(order_files)} .txt files")

    # Track SSOT_ORDER_ID values
    order_id_map: Dict[str, List[str]] = {}
    empty_files = []
    missing_id_files = []

    for file in sorted(order_files):
        # Check for empty files
        if file.stat().st_size == 0:
            empty_files.append(file.name)
            continue

        # Read file and extract SSOT_ORDER_ID
        try:
            with open(file, encoding="utf-8") as f:
                content = f.read()

            # Search for SSOT_ORDER_ID pattern
            match = re.search(r'\[SSOT_ORDER_ID\]\s+(\S+)', content)

            if match:
                order_id = match.group(1)
                if order_id not in order_id_map:
                    order_id_map[order_id] = []
                order_id_map[order_id].append(file.name)
            else:
                missing_id_files.append(file.name)

        except Exception as e:
            print(f"[WARN] Error reading {file.name}: {e}")
            missing_id_files.append(file.name)

    # Find duplicates
    duplicates = {oid: files for oid, files in order_id_map.items() if len(files) > 1}

    # Report results
    has_errors = bool(empty_files or missing_id_files or duplicates)

    if has_errors:
        print("")
        print("[FAIL] Issues detected:")

        if empty_files:
            print(f"\n  Empty files ({len(empty_files)}):")
            for f in empty_files:
                print(f"    - {f}")

        if missing_id_files:
            print(f"\n  Missing SSOT_ORDER_ID ({len(missing_id_files)}):")
            for f in missing_id_files:
                print(f"    - {f}")

        if duplicates:
            print(f"\n  Duplicate SSOT_ORDER_ID ({len(duplicates)}):")
            for oid, files in duplicates.items():
                print(f"    {oid}:")
                for f in files:
                    print(f"      - {f}")

        print("")
        sys.exit(1)
    else:
        print("")
        print("[PASS] All GPTORDER files valid!")
        print(f"  Unique SSOT_ORDER_IDs: {len(order_id_map)}")
        print(f"  Total files: {len(order_files)}")
        print("")
        sys.exit(0)


if __name__ == "__main__":
    main()
