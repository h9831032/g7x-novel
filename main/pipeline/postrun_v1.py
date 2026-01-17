#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G7X Postrun Hook v1

Runs after manager.py completes (success or failure):
1. Checks RUN artifacts using check_run_artifacts_v1.py
2. If artifacts check fails, packs to FAIL_BOX using fail_box_packer_v1.py

Preserves original exitcode.
"""
import sys
import subprocess
from pathlib import Path
from typing import Optional


def run_postrun_hook(ssot_root: Path, original_exitcode: int) -> int:
    """
    Execute postrun hooks.

    Args:
        ssot_root: SSOT root path
        original_exitcode: Manager's exitcode to preserve

    Returns:
        Original exitcode (unchanged)
    """
    print("")
    print("[POSTRUN] Running postrun hooks...")

    # Find Python executable
    python_exe = ssot_root / ".venv" / "Scripts" / "python.exe"
    if not python_exe.exists():
        python_exe = ssot_root / "v1.venv" / "Scripts" / "python.exe"

    if not python_exe.exists():
        print("[POSTRUN WARN] Python executable not found. Skipping hooks.")
        return original_exitcode

    # Hook 1: Check RUN artifacts
    check_script = ssot_root / "tools" / "check_run_artifacts_v1.py"
    if check_script.exists():
        print("[POSTRUN] Running artifact checker...")
        try:
            result = subprocess.run(
                [str(python_exe), str(check_script)],
                cwd=str(ssot_root),
                capture_output=True,
                text=True
            )

            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            # Hook 2: If artifact check failed, pack to FAIL_BOX
            if result.returncode != 0:
                print("[POSTRUN] Artifact check failed. Running FAIL_BOX packer...")
                packer_script = ssot_root / "tools" / "fail_box_packer_v1.py"

                if packer_script.exists():
                    pack_result = subprocess.run(
                        [str(python_exe), str(packer_script)],
                        cwd=str(ssot_root),
                        capture_output=True,
                        text=True
                    )

                    print(pack_result.stdout)
                    if pack_result.stderr:
                        print(pack_result.stderr, file=sys.stderr)
                else:
                    print("[POSTRUN WARN] fail_box_packer_v1.py not found.")

        except Exception as e:
            print(f"[POSTRUN ERROR] {e}", file=sys.stderr)
    else:
        print("[POSTRUN WARN] check_run_artifacts_v1.py not found. Skipping artifact check.")

    print("[POSTRUN] Hooks complete.")
    print("")

    # Preserve original exitcode
    return original_exitcode
