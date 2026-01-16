"""
G7X Integration Map Generator
메인에 붙은 컴포넌트 한눈에 보기
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def check_file_and_function(file_path, function_names):
    """파일 존재 + 함수 존재 체크"""
    if not file_path.exists():
        return "MISSING", []
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        found = [fn for fn in function_names if fn in content]
        return "EXISTS", found
    except:
        return "ERROR", []


def generate_integration_map(ssot_root):
    """통합 지도 생성"""
    root = Path(ssot_root)
    
    lines = []
    lines.append("=" * 70)
    lines.append(f"G7X Integration Map - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)
    lines.append("")
    
    # 1. MAIN ENTRY
    lines.append("[MAIN ENTRY]")
    manager_path = root / "main" / "manager.py"
    status, funcs = check_file_and_function(manager_path, ["RunManager", "main", "run"])
    lines.append(f"  main/manager.py: {status}")
    if funcs:
        lines.append(f"    Functions: {', '.join(funcs)}")
    lines.append("")
    
    # 2. EVIDENCE
    lines.append("[EVIDENCE]")
    evidence_path = root / "engine" / "evidence_writer.py"
    status, funcs = check_file_and_function(evidence_path, ["EvidenceWriter", "finalize", "write_mission_receipt"])
    lines.append(f"  engine/evidence_writer.py: {status}")
    if funcs:
        lines.append(f"    Functions: {', '.join(funcs)}")
    lines.append("")
    
    # 3. VERIFY (CHECK)
    lines.append("[VERIFY (CHECK)]")
    check_path = root / "tools" / "check_run_pack.py"
    status, funcs = check_file_and_function(check_path, ["verify_run", "check_run_pack"])
    lines.append(f"  tools/check_run_pack.py: {status}")
    if funcs:
        lines.append(f"    Functions: {', '.join(funcs)}")
    
    verify_ps1 = root / "tools" / "verify_run.ps1"
    lines.append(f"  tools/verify_run.ps1: {'EXISTS' if verify_ps1.exists() else 'MISSING'}")
    
    verify_latest_ps1 = root / "tools" / "verify_latest_run.ps1"
    lines.append(f"  tools/verify_latest_run.ps1: {'EXISTS' if verify_latest_ps1.exists() else 'MISSING'}")
    lines.append("")
    
    # 4. DEVLOG
    lines.append("[DEVLOG]")
    devlog_path = root / "tools" / "generate_devlog.py"
    status, funcs = check_file_and_function(devlog_path, ["generate_devlog", "append_devlog"])
    lines.append(f"  tools/generate_devlog.py: {status}")
    if funcs:
        lines.append(f"    Functions: {', '.join(funcs)}")
    
    devlog_dir = root / "devlog"
    lines.append(f"  devlog/ directory: {'EXISTS' if devlog_dir.exists() else 'MISSING'}")
    
    if devlog_dir.exists():
        devlog_jsonl = devlog_dir / "devlog.jsonl"
        lines.append(f"    devlog.jsonl: {'EXISTS' if devlog_jsonl.exists() else 'MISSING'}")
    lines.append("")
    
    # 5. NIGHT LOOP
    lines.append("[NIGHT LOOP]")
    night_loop = root / "tools" / "night_loop.ps1"
    lines.append(f"  tools/night_loop.ps1: {'EXISTS' if night_loop.exists() else 'MISSING'}")
    
    guard_path = root / "main" / "night_shift_guard_v5.py"
    status, funcs = check_file_and_function(guard_path, ["run_manager", "verify_run"])
    lines.append(f"  main/night_shift_guard_v5.py: {status}")
    if funcs:
        lines.append(f"    Functions: {', '.join(funcs)}")
    
    one_shot = root / "tools" / "one_shot_night_work_600.py"
    lines.append(f"  tools/one_shot_night_work_600.py: {'EXISTS' if one_shot.exists() else 'MISSING'}")
    lines.append("")
    
    # 6. ANCHOR RUN
    lines.append("[ANCHOR RUN]")
    anchor_file = root / "ANCHOR_RUN.txt"
    if anchor_file.exists():
        anchor_run = anchor_file.read_text(encoding='utf-8').strip()
        lines.append(f"  ANCHOR_RUN.txt: EXISTS")
        lines.append(f"    RUN_ID: {anchor_run}")
    else:
        lines.append(f"  ANCHOR_RUN.txt: MISSING")
    lines.append("")
    
    # 7. LATEST RUN
    lines.append("[LATEST RUN]")
    runs_dir = root / "runs"
    if runs_dir.exists():
        run_dirs = sorted(runs_dir.glob("RUN_*"), key=lambda p: p.stat().st_mtime, reverse=True)
        if run_dirs:
            latest = run_dirs[0]
            lines.append(f"  Latest: {latest.name}")
            
            # 증거팩 체크
            evidence_files = [
                "verify_report.json",
                "stamp_manifest.json",
                "final_audit.json",
                "exitcode.txt",
                "blackbox_log.jsonl",
                "api_receipt.jsonl"
            ]
            
            evidence_status = sum(1 for f in evidence_files if (latest / f).exists())
            lines.append(f"    Evidence: {evidence_status}/{len(evidence_files)}")
            
            # receipts 체크
            receipts_dir = latest / "receipts" / "mission"
            if receipts_dir.exists():
                receipts_count = len(list(receipts_dir.glob("*.json")))
                lines.append(f"    Receipts: {receipts_count}")
            else:
                lines.append(f"    Receipts: 0 (dir missing)")
        else:
            lines.append(f"  No RUN directories found")
    else:
        lines.append(f"  runs/ directory: MISSING")
    
    lines.append("")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def main():
    ssot_root = r"C:\g7core\g7_v1"
    if len(sys.argv) > 1:
        ssot_root = sys.argv[1]
    
    root = Path(ssot_root)
    if not root.exists():
        print(f"[ERROR] SSOT_ROOT not found: {ssot_root}")
        sys.exit(1)
    
    # 통합 지도 생성
    map_content = generate_integration_map(ssot_root)
    
    # 저장
    output_path = root / "integration_map.txt"
    output_path.write_text(map_content, encoding='utf-8')
    
    print(map_content)
    print(f"\n[SAVED] {output_path}")


if __name__ == "__main__":
    main()