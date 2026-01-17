#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G7X REAL30 Classifier v1

Analyzes mission content in GPTORDER files and classifies as:
- REAL: Actual work mission (content generation, analysis, writing)
- META: Administrative/system mission (testing, validation, placeholders)

Reports REAL ratio (REAL / TOTAL) for each file.
Target: REAL ratio >= 0.95 (95% real work missions)
"""
import sys
import re
from pathlib import Path

SSOT_ROOT = Path(r"C:\g7core\g7_v1")
GPTORDER_DIR = SSOT_ROOT / "GPTORDER"

# META mission indicators (lowercase patterns)
META_PATTERNS = [
    # Testing/validation
    r'\btest\b', r'\bverif', r'\bvalidat', r'\bcheck\b', r'\bsmoke\b',

    # Placeholders
    r'\bplaceholder\b', r'\bdummy\b', r'\bfiller\b', r'\bsample\b',

    # Trivial tasks
    r'\bhello world\b', r'\bcount to \d+\b', r'\blist \d+ colors\b',
    r'\bname \d+ \w+\b',

    # Explicit meta markers
    r'\bmeta\b', r'\badmin\b', r'\binternal\b', r'\bsystem\b',

    # Intentional failures
    r'\bintentional', r'\bfailbox\b', r'\bfail\b.*\btest\b',
]

# REAL mission indicators (high-quality work)
REAL_INDICATORS = [
    # Professional writing
    r'\bprofessional\b', r'\bbusiness\b', r'\bformal\b', r'\btechnical\b',

    # Content generation
    r'\barticle\b', r'\breport\b', r'\bdocument', r'\bpresentation\b',
    r'\bproposal\b', r'\banalysis\b', r'\bsummary\b',

    # Specific deliverables
    r'\bemail template\b', r'\bcode review\b', r'\bproject plan\b',
    r'\bbest practices\b', r'\bguidelines\b',

    # Depth indicators
    r'\bdetailed\b', r'\bcomprehensive\b', r'\bin-depth\b',
    r'\bexplain\b', r'\bdescribe\b', r'\banalyze\b',
]


def classify_mission(mission: str) -> str:
    """Classify a mission as REAL or META"""
    mission_lower = mission.lower()

    # Check META patterns
    for pattern in META_PATTERNS:
        if re.search(pattern, mission_lower):
            return "META"

    # Check REAL indicators (bonus score)
    real_score = 0
    for pattern in REAL_INDICATORS:
        if re.search(pattern, mission_lower):
            real_score += 1

    # Heuristic: If multiple REAL indicators, definitely REAL
    if real_score >= 2:
        return "REAL"

    # Default: Assume REAL (benefit of doubt)
    # Short, simple missions are still work missions
    return "REAL"


def extract_missions(file_path: Path) -> list:
    """Extract mission lines (excluding header)"""
    with open(file_path, "r", encoding="utf-8") as f:
        all_lines = f.readlines()

    missions = []
    in_header = True

    for line in all_lines:
        line = line.strip()
        if not line:
            continue

        if in_header:
            if line.startswith("[") or line.startswith("-"):
                continue
            else:
                in_header = False

        if not in_header:
            missions.append(line)

    return missions


def main():
    print("[CLASSIFIER] Analyzing GPTORDER files for REAL ratio...")
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

    # Analyze each file
    results = []
    low_ratio_files = []

    for file_path in order_files:
        missions = extract_missions(file_path)
        if not missions:
            continue

        real_count = 0
        meta_count = 0

        for mission in missions:
            classification = classify_mission(mission)
            if classification == "REAL":
                real_count += 1
            else:
                meta_count += 1

        total = len(missions)
        real_ratio = real_count / total if total > 0 else 0.0

        results.append({
            "file": file_path.name,
            "total": total,
            "real": real_count,
            "meta": meta_count,
            "ratio": real_ratio
        })

        # Flag low ratio files
        if real_ratio < 0.95:
            low_ratio_files.append(file_path.name)

    # Display results
    print("========================================")
    print("REAL Ratio Analysis")
    print("========================================")
    print(f"{'File':<50} {'Total':<8} {'REAL':<8} {'META':<8} {'Ratio':<8}")
    print("-" * 82)

    for result in sorted(results, key=lambda x: x['ratio']):
        ratio_str = f"{result['ratio']:.2%}"
        status = "[OK]" if result['ratio'] >= 0.95 else "[LOW]"

        print(f"{result['file']:<50} {result['total']:<8} {result['real']:<8} {result['meta']:<8} {ratio_str:<8} {status}")

    print("")
    print("========================================")
    print("Summary")
    print("========================================")
    print(f"Files analyzed: {len(results)}")
    print(f"Low REAL ratio files (<95%): {len(low_ratio_files)}")

    if low_ratio_files:
        print("")
        print("[WARNING] Files with low REAL ratio:")
        for filename in low_ratio_files:
            print(f"  - {filename}")

        print("")
        print("[ACTION] Consider reviewing these files:")
        print("  1. Remove META/test missions")
        print("  2. Replace with real work missions")
        print("  3. Or reclassify as TEST_* if intentional")

        sys.exit(1)
    else:
        print("[PASS] All files meet REAL ratio target (>=95%)")
        sys.exit(0)


if __name__ == "__main__":
    main()
