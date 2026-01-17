#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G7X Order Duplication Audit v1

Scans GPTORDER directory for:
1. Duplicate GPTORDER files (identical content, different names)
2. Pair duplication (e.g., REAL24_DAY_S1 and REAL24_NIGHT_S1 with same missions)
3. Mission line overlap across files

Reports findings for cleanup.
"""
import sys
import hashlib
from pathlib import Path
from collections import defaultdict

SSOT_ROOT = Path(r"C:\g7core\g7_v1")
GPTORDER_DIR = SSOT_ROOT / "GPTORDER"


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file content"""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def compute_content_hash(lines: list) -> str:
    """Compute hash of mission lines only (excluding header)"""
    content = "\n".join(lines)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def extract_missions(file_path: Path) -> list:
    """Extract mission lines (excluding header and metadata)"""
    with open(file_path, "r", encoding="utf-8") as f:
        all_lines = f.readlines()

    # Skip header section (lines starting with [ or -)
    missions = []
    in_header = True

    for line in all_lines:
        line = line.strip()
        if not line:
            continue

        # Detect end of header
        if in_header:
            if line.startswith("[") or line.startswith("-"):
                continue
            else:
                in_header = False

        # Mission line
        if not in_header:
            missions.append(line)

    return missions


def main():
    print("[AUDIT] Starting order duplication audit...")
    print("")

    # Find all GPTORDER files
    order_files = sorted([
        f for f in GPTORDER_DIR.glob("*.txt")
        if f.name.startswith(("REAL", "TEST", "GPTORDER"))
    ])

    if not order_files:
        print("[WARN] No GPTORDER files found")
        sys.exit(0)

    print(f"[INFO] Found {len(order_files)} GPTORDER files")
    print("")

    # === Check 1: Identical Files (Same Full Hash) ===
    print("[CHECK 1] Scanning for identical files (full hash)...")
    file_hashes = defaultdict(list)

    for file_path in order_files:
        file_hash = compute_file_hash(file_path)
        file_hashes[file_hash].append(file_path.name)

    duplicates_found = False
    for file_hash, files in file_hashes.items():
        if len(files) > 1:
            duplicates_found = True
            print(f"[DUPLICATE] {len(files)} files with identical content:")
            for filename in files:
                print(f"  - {filename}")
            print(f"  Hash: {file_hash[:16]}...")
            print("")

    if not duplicates_found:
        print("[PASS] No identical files found")
    print("")

    # === Check 2: Mission Content Duplication ===
    print("[CHECK 2] Scanning for mission content duplication...")
    content_hashes = defaultdict(list)

    for file_path in order_files:
        missions = extract_missions(file_path)
        if missions:
            content_hash = compute_content_hash(missions)
            content_hashes[content_hash].append({
                "file": file_path.name,
                "count": len(missions)
            })

    content_dups_found = False
    for content_hash, file_data in content_hashes.items():
        if len(file_data) > 1:
            content_dups_found = True
            print(f"[DUPLICATE_CONTENT] {len(file_data)} files with identical missions:")
            for data in file_data:
                print(f"  - {data['file']} ({data['count']} missions)")
            print(f"  Content hash: {content_hash[:16]}...")
            print("")

    if not content_dups_found:
        print("[PASS] No mission content duplication found")
    print("")

    # === Check 3: Pair Analysis (DAY vs NIGHT for same slice) ===
    print("[CHECK 3] Analyzing DAY/NIGHT pair duplication...")
    pairs = defaultdict(dict)

    # Group by base name and slice
    for file_path in order_files:
        name = file_path.name
        if "_DAY_S" in name or "_NIGHT_S" in name:
            # Extract base and slice
            if "_DAY_S" in name:
                base, rest = name.split("_DAY_S")
                slice_num = rest.split("_")[0] if "_" in rest else rest.replace(".txt", "")
                profile = "DAY"
            elif "_NIGHT_S" in name:
                base, rest = name.split("_NIGHT_S")
                slice_num = rest.split("_")[0] if "_" in rest else rest.replace(".txt", "")
                profile = "NIGHT"

            key = f"{base}_S{slice_num}"
            pairs[key][profile] = {
                "file": file_path.name,
                "missions": extract_missions(file_path)
            }

    pair_issues_found = False
    for key, profiles in pairs.items():
        if "DAY" in profiles and "NIGHT" in profiles:
            day_missions = profiles["DAY"]["missions"]
            night_missions = profiles["NIGHT"]["missions"]

            if day_missions == night_missions:
                pair_issues_found = True
                print(f"[PAIR_DUPLICATE] {key}:")
                print(f"  DAY:   {profiles['DAY']['file']} ({len(day_missions)} missions)")
                print(f"  NIGHT: {profiles['NIGHT']['file']} ({len(night_missions)} missions)")
                print(f"  Status: IDENTICAL missions (should differ or be same by design?)")
                print("")

    if not pair_issues_found:
        print("[PASS] No unexpected DAY/NIGHT pair duplication")
    print("")

    # === Check 4: Mission Line Overlap ===
    print("[CHECK 4] Scanning for mission line overlap across files...")
    mission_index = defaultdict(list)

    for file_path in order_files:
        missions = extract_missions(file_path)
        for mission in missions:
            mission_index[mission].append(file_path.name)

    overlap_found = False
    for mission, files in mission_index.items():
        if len(files) > 1:
            overlap_found = True
            print(f"[OVERLAP] Mission appears in {len(files)} files:")
            print(f"  Mission: {mission[:80]}...")
            for filename in files[:5]:  # Show first 5
                print(f"  - {filename}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more files")
            print("")

    if not overlap_found:
        print("[PASS] No mission line overlap detected")
    print("")

    # === Summary ===
    print("========================================")
    print("Audit Summary")
    print("========================================")
    print(f"Files scanned: {len(order_files)}")
    print(f"Identical files: {'YES' if duplicates_found else 'NO'}")
    print(f"Content duplication: {'YES' if content_dups_found else 'NO'}")
    print(f"Pair issues: {'YES' if pair_issues_found else 'NO'}")
    print(f"Mission overlap: {'YES' if overlap_found else 'NO'}")
    print("========================================")

    if duplicates_found or content_dups_found:
        print("[ACTION] Consider removing duplicate files")
        sys.exit(1)
    else:
        print("[PASS] No critical duplication found")
        sys.exit(0)


if __name__ == "__main__":
    main()
