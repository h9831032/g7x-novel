"""
DEVLOG Auto Writer v2
Execution complete -> 5 files auto generation
Fix: DEVLOG folder uppercase, Gemini 2.0 Flash model support
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


def get_latest_run(runs_dir: Path) -> Path:
    """Get latest RUN folder"""
    runs = [d for d in runs_dir.iterdir() if d.is_dir() and d.name.startswith("RUN_")]
    if not runs:
        raise FileNotFoundError("No RUN folders found")
    return max(runs, key=lambda p: p.stat().st_mtime)


def read_evidence(run_path: Path) -> Dict[str, Any]:
    """Read evidence files from RUN"""
    evidence = {
        "run_id": run_path.name,
        "exitcode": None,
        "expected": 0,
        "done": 0,
        "verdict": "UNKNOWN",
        "stderr_exists": False,
        "errors": []
    }
    
    exitcode_file = run_path / "exitcode.txt"
    if exitcode_file.exists():
        try:
            evidence["exitcode"] = int(exitcode_file.read_text().strip())
        except Exception:
            pass
    
    verify_file = run_path / "verify_report.json"
    if verify_file.exists():
        try:
            data = json.loads(verify_file.read_text(encoding="utf-8"))
            evidence["expected"] = data.get("expected_missions", 0)
            evidence["done"] = data.get("done_missions", 0)
            evidence["verdict"] = "PASS" if data.get("pass", False) else "FAIL"
        except Exception:
            pass
    
    final_audit_file = run_path / "final_audit.json"
    if final_audit_file.exists():
        try:
            data = json.loads(final_audit_file.read_text(encoding="utf-8"))
            if not evidence["done"]:
                evidence["done"] = data.get("done_missions", 0)
        except Exception:
            pass
    
    stderr_file = run_path / "stderr_manager.txt"
    evidence["stderr_exists"] = stderr_file.exists()
    
    if stderr_file.exists() and stderr_file.stat().st_size > 0:
        try:
            lines = stderr_file.read_text(encoding="utf-8").splitlines()
            evidence["errors"] = lines[-3:] if len(lines) >= 3 else lines
        except Exception:
            pass
    
    return evidence


def scan_delta_files(ssot_root: Path, since_hours: int = 24) -> List[str]:
    """Scan recently modified files"""
    cutoff = datetime.now().timestamp() - (since_hours * 3600)
    delta = []
    
    for ext in [".py", ".ps1", ".txt", ".json", ".jsonl"]:
        for f in ssot_root.rglob(f"*{ext}"):
            if f.is_file() and f.stat().st_mtime > cutoff:
                try:
                    rel_path = f.relative_to(ssot_root)
                    delta.append(str(rel_path))
                except ValueError:
                    continue
    
    return sorted(delta)[:30]


def build_seed_map(ssot_root: Path) -> Dict[str, Any]:
    """Build initial integration map from current code"""
    seed = {
        "timestamp": datetime.now().isoformat(),
        "root": str(ssot_root),
        "nodes": {}
    }
    
    manager_path = ssot_root / "main" / "manager.py"
    if manager_path.exists():
        seed["nodes"]["manager"] = {
            "path": str(manager_path.relative_to(ssot_root)),
            "status": "WELDED",
            "role": "main_entry"
        }
        
        try:
            content = manager_path.read_text(encoding="utf-8")
            if "evidence" in content.lower():
                seed["nodes"]["evidence_writer"] = {
                    "path": "main/pipeline/evidence.py",
                    "status": "WIRED",
                    "role": "evidence_generation"
                }
            if "catalog" in content.lower():
                seed["nodes"]["catalog"] = {
                    "path": "main/pipeline/catalog.py",
                    "status": "WIRED",
                    "role": "order_compilation"
                }
            if "runner" in content.lower():
                seed["nodes"]["runner"] = {
                    "path": "main/pipeline/runner.py",
                    "status": "WIRED",
                    "role": "mission_execution"
                }
        except Exception:
            pass
    
    return seed


def write_daily_report(
    devlog_dir: Path,
    date_str: str,
    evidence: Dict[str, Any],
    delta: List[str],
    seed_map: Dict[str, Any]
) -> Path:
    """Write human-readable daily report"""
    
    day_dir = devlog_dir / date_str
    day_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = day_dir / f"DAILY_REPORT_{date_str}.txt"
    
    content = f"""G7X DAILY REPORT - {date_str}

=== EVIDENCE (Latest RUN) ===
RUN ID: {evidence['run_id']}
Exitcode: {evidence['exitcode']}
Expected: {evidence['expected']}
Done: {evidence['done']}
Verdict: {evidence['verdict']}
Stderr Exists: {evidence['stderr_exists']}

Representative Errors (last 3 lines):
"""
    
    if evidence['errors']:
        for line in evidence['errors']:
            content += f"  {line}\n"
    else:
        content += "  (none)\n"
    
    content += f"""
=== DELTA (Today's Changes) ===
Total Files Modified: {len(delta)}
Top 30:
"""
    
    for f in delta[:30]:
        content += f"  - {f}\n"
    
    content += f"""
=== INTEGRATION MAP (Snapshot) ===
"""
    
    for node_name, node_data in seed_map.get("nodes", {}).items():
        content += f"  [{node_data['status']}] {node_name} -> {node_data['path']}\n"
    
    content += """
=== NEXT (Tomorrow) ===
Main Tasks (Day):
  1. Verify DEVLOG auto-generation stability
  2. Review evidence layer completeness
  3. Check integration map accuracy

Night Tasks:
  1. Execute REAL_WORK_120 batch
  2. Monitor FAIL_BOX isolation
  3. Validate retry order generation
"""
    
    report_path.write_text(content, encoding="utf-8")
    return report_path


def write_evidence_latest(devlog_dir: Path, evidence: Dict[str, Any]) -> Path:
    """Write EVIDENCE_LATEST.json"""
    path = devlog_dir / "EVIDENCE_LATEST.json"
    path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_delta_today(devlog_dir: Path, delta: List[str]) -> Path:
    """Write DELTA_TODAY.json"""
    path = devlog_dir / "DELTA_TODAY.json"
    data = {
        "timestamp": datetime.now().isoformat(),
        "count": len(delta),
        "files": delta
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_next_tomorrow(devlog_dir: Path) -> Path:
    """Write NEXT_TOMORROW.json"""
    path = devlog_dir / "NEXT_TOMORROW.json"
    data = {
        "timestamp": datetime.now().isoformat(),
        "main_tasks": [
            "Verify DEVLOG auto-generation stability",
            "Review evidence layer completeness",
            "Check integration map accuracy"
        ],
        "night_tasks": [
            "Execute REAL_WORK_120 batch with Gemini 2.0 Flash",
            "Monitor FAIL_BOX isolation",
            "Validate retry order generation"
        ]
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_integration_map(devlog_dir: Path, seed_map: Dict[str, Any]) -> Path:
    """Write INTEGRATION_MAP.json (cumulative)"""
    path = devlog_dir / "INTEGRATION_MAP.json"
    
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            for node_name, node_data in seed_map.get("nodes", {}).items():
                if node_name not in existing.get("nodes", {}):
                    existing["nodes"][node_name] = node_data
            existing["timestamp"] = datetime.now().isoformat()
            seed_map = existing
        except Exception:
            pass
    
    path.write_text(json.dumps(seed_map, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def generate_devlog_5files(ssot_root: Path) -> Dict[str, Path]:
    """
    Main entry: Generate 5 DEVLOG files
    Returns: dict of file paths
    """
    ssot_root = Path(ssot_root)
    devlog_dir = ssot_root / "DEVLOG"
    devlog_dir.mkdir(exist_ok=True)
    
    runs_dir = ssot_root / "runs"
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    latest_run = get_latest_run(runs_dir)
    
    evidence = read_evidence(latest_run)
    delta = scan_delta_files(ssot_root)
    seed_map = build_seed_map(ssot_root)
    
    files = {}
    files["daily_report"] = write_daily_report(devlog_dir, date_str, evidence, delta, seed_map)
    files["evidence_latest"] = write_evidence_latest(devlog_dir, evidence)
    files["delta_today"] = write_delta_today(devlog_dir, delta)
    files["next_tomorrow"] = write_next_tomorrow(devlog_dir)
    files["integration_map"] = write_integration_map(devlog_dir, seed_map)
    
    return files


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python devlog_writer.py <ssot_root>")
        sys.exit(1)
    
    ssot_root = Path(sys.argv[1])
    
    try:
        files = generate_devlog_5files(ssot_root)
        print("[DEVLOG] Generated 5 files:")
        for name, path in files.items():
            print(f"  {name}: {path}")
    except Exception as e:
        print(f"[DEVLOG ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
