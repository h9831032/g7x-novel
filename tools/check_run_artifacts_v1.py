#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G7X RUN Artifacts Checker v1

Finds the latest RUN folder in runs/ and checks for required evidence files:
- verify_report.json
- stamp_manifest.json (or hash_manifest.json)
- exitcode.txt
- stdout_manager.txt
- stderr_manager.txt
- final_audit.json (or audit_receipt.json)

Reports PASS/FAIL with missing artifacts list.
"""
import sys
from pathlib import Path

SSOT_ROOT = Path(r"C:\g7core\g7_v1")
RUNS_DIR = SSOT_ROOT / "runs"

# Required artifacts
REQUIRED_ARTIFACTS = [
    "verify_report.json",
    "exitcode.txt",
    "stdout_manager.txt",
    "stderr_manager.txt"
]

# Alternative artifacts (at least one must exist)
MANIFEST_ALTERNATIVES = ["stamp_manifest.json", "hash_manifest.json"]
AUDIT_ALTERNATIVES = ["final_audit.json", "audit_receipt.json"]


def fail_fast(msg: str):
    print(f"[FAIL] {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    print("[RUN_ARTIFACTS] Checking latest RUN folder...")

    # 1. Check runs directory exists
    if not RUNS_DIR.exists():
        fail_fast(f"runs directory not found: {RUNS_DIR}")

    # 2. Find latest RUN folder (sorted by name, assumes RUN_YYYYMMDD_HHMMSS format)
    run_folders = sorted([d for d in RUNS_DIR.iterdir() if d.is_dir() and d.name.startswith("RUN_")])

    if not run_folders:
        fail_fast("No RUN folders found in runs/")

    latest_run = run_folders[-1]
    print(f"[INFO] Latest RUN: {latest_run.name}")
    print("")

    # 3. Check required artifacts
    missing = []

    for artifact in REQUIRED_ARTIFACTS:
        artifact_path = latest_run / artifact
        if not artifact_path.exists():
            missing.append(artifact)

    # 4. Check manifest alternatives (at least one must exist)
    manifest_found = any((latest_run / alt).exists() for alt in MANIFEST_ALTERNATIVES)
    if not manifest_found:
        missing.append(f"({' or '.join(MANIFEST_ALTERNATIVES)})")

    # 5. Check audit alternatives (at least one must exist)
    audit_found = any((latest_run / alt).exists() for alt in AUDIT_ALTERNATIVES)
    if not audit_found:
        missing.append(f"({' or '.join(AUDIT_ALTERNATIVES)})")

    # 6. [VERIFY_MIN] Check file content (not just existence)
    verify_min_fails = []

    # exitcode.txt must contain valid integer
    exitcode_file = latest_run / "exitcode.txt"
    if exitcode_file.exists():
        try:
            exitcode_value = int(exitcode_file.read_text().strip())
            print(f"[VERIFY_MIN] exitcode={exitcode_value}")
        except ValueError:
            verify_min_fails.append("exitcode.txt contains invalid integer")

    # stdout/stderr must exist (even if 0 bytes)
    stdout_file = latest_run / "stdout_manager.txt"
    stderr_file = latest_run / "stderr_manager.txt"

    if not stdout_file.exists():
        verify_min_fails.append("stdout_manager.txt missing")
    if not stderr_file.exists():
        verify_min_fails.append("stderr_manager.txt missing")

    # 7. HARD FAIL if verify_min fails
    if verify_min_fails:
        print("[HARD FAIL] verify_min check failed:")
        for fail in verify_min_fails:
            print(f"  - {fail}")
        print("")
        print(f"RUN_PATH: {latest_run}")
        sys.exit(1)

    # 8. Report results
    if missing:
        print("[FAIL] Missing artifacts:")
        for item in missing:
            print(f"  - {item}")
        print("")
        print(f"RUN_PATH: {latest_run}")
        sys.exit(1)
    else:
        print("[PASS] All required artifacts present!")
        print("[VERIFY_MIN] PASS - Files exist and valid")
        print("")
        print("Found artifacts:")
        for artifact in REQUIRED_ARTIFACTS:
            print(f"  OK {artifact}")

        # Show which alternatives were found
        for alt in MANIFEST_ALTERNATIVES:
            if (latest_run / alt).exists():
                print(f"  OK {alt}")
                break

        for alt in AUDIT_ALTERNATIVES:
            if (latest_run / alt).exists():
                print(f"  OK {alt}")
                break

        print("")
        print(f"RUN_PATH: {latest_run}")
        sys.exit(0)


if __name__ == "__main__":
    main()
