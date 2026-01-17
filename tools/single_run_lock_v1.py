#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G7X Single Run Lock v1

Ensures only one manager.py instance runs at a time.
Uses a lock file to prevent concurrent execution.

Usage:
    # Acquire lock before running manager
    python tools/single_run_lock_v1.py --acquire

    # Release lock after manager completes
    python tools/single_run_lock_v1.py --release

    # Check lock status
    python tools/single_run_lock_v1.py --status
"""
import sys
import os
import time
from pathlib import Path
import argparse

SSOT_ROOT = Path(r"C:\g7core\g7_v1")
LOCK_FILE = SSOT_ROOT / "STATE_PACK" / "RUN_LOCK.txt"
LOCK_TIMEOUT = 3600  # 1 hour timeout for stale locks


def acquire_lock():
    """Acquire run lock. Exits with 1 if lock already held."""
    LOCK_FILE.parent.mkdir(exist_ok=True)

    # Check if lock exists
    if LOCK_FILE.exists():
        # Check lock age (detect stale locks)
        lock_age = time.time() - LOCK_FILE.stat().st_mtime

        if lock_age > LOCK_TIMEOUT:
            print(f"[LOCK] Stale lock detected (age: {lock_age:.0f}s), removing")
            LOCK_FILE.unlink()
        else:
            # Read lock info
            lock_info = LOCK_FILE.read_text(encoding="utf-8").strip()
            print(f"[LOCK_FAIL] Another run is in progress", file=sys.stderr)
            print(f"[LOCK_FAIL] Lock info: {lock_info}", file=sys.stderr)
            print(f"[LOCK_FAIL] Lock age: {lock_age:.0f}s", file=sys.stderr)
            print(f"[LOCK_FAIL] To force release: python tools/single_run_lock_v1.py --release", file=sys.stderr)
            sys.exit(1)

    # Acquire lock
    lock_data = f"pid={os.getpid()}\ntime={time.time()}\nhost={os.environ.get('COMPUTERNAME', 'unknown')}\n"
    LOCK_FILE.write_text(lock_data, encoding="utf-8")
    print(f"[LOCK] Acquired (pid={os.getpid()})")
    sys.exit(0)


def release_lock():
    """Release run lock."""
    if LOCK_FILE.exists():
        lock_info = LOCK_FILE.read_text(encoding="utf-8").strip()
        LOCK_FILE.unlink()
        print(f"[LOCK] Released")
        print(f"[LOCK] Previous lock: {lock_info}")
        sys.exit(0)
    else:
        print(f"[LOCK] No lock file found (already released)")
        sys.exit(0)


def check_status():
    """Check lock status."""
    if LOCK_FILE.exists():
        lock_info = LOCK_FILE.read_text(encoding="utf-8").strip()
        lock_age = time.time() - LOCK_FILE.stat().st_mtime

        print(f"[LOCK] Status: LOCKED")
        print(f"[LOCK] Info: {lock_info}")
        print(f"[LOCK] Age: {lock_age:.0f}s")

        if lock_age > LOCK_TIMEOUT:
            print(f"[LOCK] WARNING: Stale lock (age > {LOCK_TIMEOUT}s)")
            sys.exit(1)
        else:
            sys.exit(0)
    else:
        print(f"[LOCK] Status: UNLOCKED")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="G7X Single Run Lock")
    parser.add_argument("--acquire", action="store_true", help="Acquire run lock")
    parser.add_argument("--release", action="store_true", help="Release run lock")
    parser.add_argument("--status", action="store_true", help="Check lock status")

    args = parser.parse_args()

    if args.acquire:
        acquire_lock()
    elif args.release:
        release_lock()
    elif args.status:
        check_status()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
