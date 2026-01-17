#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G7X Compiler Guard v1

Validates order files before execution:
- Check for empty lines
- Check for duplicate lines
- Check line count sanity
- Check file format validity

FAIL_FAST if any validation fails.
"""
import sys
from pathlib import Path
from typing import List, Tuple


def validate_order_file(order_path: Path) -> Tuple[bool, str]:
    """
    Validate order file before execution.

    Returns:
        (success, error_message)
    """
    if not order_path.exists():
        return False, f"Order file not found: {order_path}"

    if order_path.stat().st_size == 0:
        return False, f"Order file is empty: {order_path}"

    # Read all lines
    try:
        with open(order_path, encoding="utf-8") as f:
            lines = [line.rstrip("\n") for line in f]
    except Exception as e:
        return False, f"Error reading file: {e}"

    # Remove trailing empty lines
    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        return False, "Order file contains no valid lines"

    # Check for empty lines in the middle
    empty_line_indices = [i + 1 for i, line in enumerate(lines) if not line.strip()]
    if empty_line_indices:
        return False, f"Empty lines found at: {empty_line_indices}"

    # Check for duplicate lines
    seen = set()
    duplicates = []
    for i, line in enumerate(lines):
        if line in seen:
            duplicates.append((i + 1, line[:50]))  # First 50 chars
        seen.add(line)

    if duplicates:
        dup_summary = "; ".join([f"line {idx}" for idx, _ in duplicates[:5]])
        return False, f"Duplicate lines found: {dup_summary}"

    # Sanity check: reasonable line count (1-100 missions)
    if len(lines) > 100:
        return False, f"Too many lines: {len(lines)} (max 100)"

    # All checks passed
    return True, f"Valid: {len(lines)} missions"


def run_compiler_guard(order_path: Path) -> None:
    """
    Run compiler guard and exit on failure.

    Args:
        order_path: Path to order file

    Raises:
        SystemExit: If validation fails
    """
    print(f"[COMPILER_GUARD] Validating order file: {order_path.name}")

    success, message = validate_order_file(order_path)

    if not success:
        print(f"[COMPILER_GUARD FAIL] {message}")
        print("[FAIL_FAST] Exiting due to invalid order file.")
        sys.exit(1)

    print(f"[COMPILER_GUARD PASS] {message}")
