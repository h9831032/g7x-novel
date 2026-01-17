#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G7X NEXT_TOP10 Builder v1

Reads tracker files (ISSUES, ACTIONS, DECISIONS) and creates
NEXT_TOP10.json with prioritized next actions.
"""
import sys
import json
from pathlib import Path

SSOT_ROOT = Path(r"C:\g7core\g7_v1")
DEVLOG_DIR = SSOT_ROOT / "DEVLOG"
OUTPUT_FILE = DEVLOG_DIR / "NEXT_TOP10.json"


def main():
    print("[NEXT_TOP10] Building NEXT_TOP10.json...")

    # Create DEVLOG directory if not exists
    DEVLOG_DIR.mkdir(exist_ok=True)

    # Collect items from tracker files (if they exist)
    next_items = []

    # Check for ISSUES_2026-01.tsv
    issues_file = SSOT_ROOT / "ISSUES_2026-01.tsv"
    if issues_file.exists():
        next_items.extend(parse_issues(issues_file))

    # Check for ACTIONS_2026-01.tsv
    actions_file = SSOT_ROOT / "ACTIONS_2026-01.tsv"
    if actions_file.exists():
        next_items.extend(parse_actions(actions_file))

    # Check for DECISIONS_2026-01.jsonl
    decisions_file = SSOT_ROOT / "DECISIONS_2026-01.jsonl"
    if decisions_file.exists():
        next_items.extend(parse_decisions(decisions_file))

    # If no tracker files, create default items
    if not next_items:
        next_items = create_default_items()

    # Sort by priority and take top 10
    next_items.sort(key=lambda x: x["priority"], reverse=True)
    top10 = next_items[:10]

    # Write to output file
    output_data = {
        "generated_at": Path(__file__).stat().st_mtime,
        "count": len(top10),
        "items": top10
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] NEXT_TOP10.json created with {len(top10)} items")
    print(f"  Path: {OUTPUT_FILE}")


def parse_issues(file_path):
    """Parse ISSUES TSV file."""
    items = []
    # Simplified parser - just create placeholder
    items.append({
        "id": "ISSUE_001",
        "title": "Track issues from ISSUES_2026-01.tsv",
        "priority": 5,
        "reason": "Issue tracking active"
    })
    return items


def parse_actions(file_path):
    """Parse ACTIONS TSV file."""
    items = []
    items.append({
        "id": "ACTION_001",
        "title": "Track actions from ACTIONS_2026-01.tsv",
        "priority": 6,
        "reason": "Action tracking active"
    })
    return items


def parse_decisions(file_path):
    """Parse DECISIONS JSONL file."""
    items = []
    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    decision = json.loads(line)
                    items.append({
                        "id": decision.get("id", "DECISION_UNKNOWN"),
                        "title": decision.get("title", "Untitled decision"),
                        "priority": decision.get("priority", 5),
                        "reason": decision.get("reason", "Decision logged")
                    })
    except Exception as e:
        print(f"[WARN] Error parsing decisions: {e}")
    return items


def create_default_items():
    """Create default NEXT items when no trackers exist."""
    return [
        {
            "id": "DEFAULT_001",
            "title": "Continue GPTORDER execution",
            "priority": 10,
            "reason": "Execute remaining GPTORDER files"
        },
        {
            "id": "DEFAULT_002",
            "title": "Run REAL36 missions",
            "priority": 9,
            "reason": "Execute REAL mode missions"
        },
        {
            "id": "DEFAULT_003",
            "title": "Verify evidence packs",
            "priority": 8,
            "reason": "Check RUN artifacts integrity"
        }
    ]


if __name__ == "__main__":
    main()
