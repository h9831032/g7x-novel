#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G7X REAL24 Slice Builder v1

Reads REAL24_REAL_A.txt (24 lines) and splits into:
- REAL24_DAY_S1.txt ~ S4.txt (4 slices, 6 lines each)
- REAL24_NIGHT_S1.txt ~ S4.txt (4 slices, 6 lines each)

FAIL_FAST on:
- Line count != 24
- Empty lines
- Duplicate lines
"""
import sys
from pathlib import Path

SSOT_ROOT = Path(r"C:\g7core\g7_v1")
GPTORDER_DIR = SSOT_ROOT / "GPTORDER"
SOURCE_FILE = GPTORDER_DIR / "REAL24_REAL_A.txt"

SLICE_SIZE = 6  # 6 missions per slice
EXPECTED_LINES = 24  # 4 slices * 6 lines


def fail_fast(msg: str):
    print(f"[FAIL] {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    print("[REAL24_SLICES] Starting slice generation...")

    # 1. Check source file exists
    if not SOURCE_FILE.exists():
        fail_fast(f"Source file not found: {SOURCE_FILE}")

    # 2. Read all lines
    with open(SOURCE_FILE, encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    print(f"[INFO] Read {len(lines)} lines from {SOURCE_FILE.name}")

    # 3. Validate line count
    if len(lines) != EXPECTED_LINES:
        fail_fast(f"Expected {EXPECTED_LINES} lines, got {len(lines)}")

    # 4. Check for empty lines
    empty_lines = [i + 1 for i, line in enumerate(lines) if not line.strip()]
    if empty_lines:
        fail_fast(f"Empty lines found at: {empty_lines}")

    # 5. Check for duplicates
    seen = set()
    duplicates = []
    for i, line in enumerate(lines):
        if line in seen:
            duplicates.append((i + 1, line))
        seen.add(line)

    if duplicates:
        fail_fast(f"Duplicate lines found: {duplicates}")

    # 6. Split into 4 slices (6 lines each)
    slices = []
    for i in range(4):
        start_idx = i * SLICE_SIZE
        end_idx = start_idx + SLICE_SIZE
        slice_lines = lines[start_idx:end_idx]
        slices.append(slice_lines)

    # 7. Write DAY slices
    for i, slice_lines in enumerate(slices):
        day_file = GPTORDER_DIR / f"REAL24_DAY_S{i + 1}.txt"
        with open(day_file, "w", encoding="utf-8") as f:
            f.write("\n".join(slice_lines) + "\n")
        print(f"[DAY] Created {day_file.name} ({len(slice_lines)} lines)")

    # 8. Write NIGHT slices (same content, different profile)
    for i, slice_lines in enumerate(slices):
        night_file = GPTORDER_DIR / f"REAL24_NIGHT_S{i + 1}.txt"
        with open(night_file, "w", encoding="utf-8") as f:
            f.write("\n".join(slice_lines) + "\n")
        print(f"[NIGHT] Created {night_file.name} ({len(slice_lines)} lines)")

    print("")
    print("[SUCCESS] All REAL24 slices created!")
    print(f"  DAY: REAL24_DAY_S1.txt ~ S4.txt")
    print(f"  NIGHT: REAL24_NIGHT_S1.txt ~ S4.txt")
    print(f"  Total: 8 files, {EXPECTED_LINES} missions")


if __name__ == "__main__":
    main()
