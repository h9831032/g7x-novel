#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G7X STOP Gate v1

Checks STATE_PACK/CHECKPOINT_LATEST.txt before batch execution.
Returns PASS if checkpoint indicates ready status, FAIL otherwise.

Usage:
    python stop_gate_v1.py [--batch S2]
"""
import sys
from pathlib import Path
import argparse

SSOT_ROOT = Path(r"C:\g7core\g7_v1")
CHECKPOINT_FILE = SSOT_ROOT / "STATE_PACK" / "CHECKPOINT_LATEST.txt"


def fail_fast(msg: str):
    print(f"[STOP_GATE_FAIL] {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="G7X STOP Gate")
    parser.add_argument("--batch", type=str, help="Expected batch ID (e.g., S2)")
    args = parser.parse_args()

    print("[STOP_GATE] Checking checkpoint status...")

    # 1. Check checkpoint file exists
    if not CHECKPOINT_FILE.exists():
        fail_fast(f"Checkpoint file not found: {CHECKPOINT_FILE}")

    # 2. Read checkpoint
    try:
        content = CHECKPOINT_FILE.read_text(encoding="utf-8")
    except Exception as e:
        fail_fast(f"Cannot read checkpoint file: {e}")

    print(f"[STOP_GATE] Checkpoint content:")
    print(content)
    print("")

    # 3. Parse checkpoint (simple key:value parsing)
    checkpoint_data = {}
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            checkpoint_data[key.strip()] = value.strip()

    # 4. Validate checkpoint
    status = checkpoint_data.get("status", "UNKNOWN")
    exitcode = checkpoint_data.get("exitcode", "UNKNOWN")
    run_path = checkpoint_data.get("run_path", "UNKNOWN")

    print(f"[STOP_GATE] Parsed checkpoint:")
    print(f"  status: {status}")
    print(f"  exitcode: {exitcode}")
    print(f"  run_path: {run_path}")

    # 5. Check if batch matches (if specified)
    if args.batch:
        next_batch = checkpoint_data.get("next_batch", "UNKNOWN")
        if next_batch != args.batch:
            fail_fast(f"Batch mismatch: checkpoint says next_batch={next_batch}, but requested {args.batch}")
        print(f"[STOP_GATE] Batch validation: {args.batch} MATCH")

    # 6. Check status
    if "FAIL" in status:
        fail_fast(f"Previous run FAILED with status: {status}")

    if exitcode not in ["0", "UNKNOWN"]:
        fail_fast(f"Previous run had non-zero exitcode: {exitcode}")

    # 7. PASS
    print("[STOP_GATE] PASS - Ready to proceed")
    print("")
    sys.exit(0)


if __name__ == "__main__":
    main()
