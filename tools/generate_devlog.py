"""
G7X Devlog Generator
개발일지 자동 생성 (txt + jsonl)
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime


def generate_devlog_entry(run_path, ssot_root):
    """RUN 기반 devlog 엔트리 생성"""
    run_dir = Path(run_path)
    root = Path(ssot_root)
    
    if not run_dir.exists():
        return None
    
    entry = {
        "run_id": run_dir.name,
        "timestamp": datetime.now().isoformat(),
        "start_time": None,
        "end_time": None,
        "duration_sec": 0,
        "order_path": "UNKNOWN",
        "expected_missions": 0,
        "done_missions": 0,
        "api_error_count": 0,
        "exitcode": 999,
        "pass_bool": False,
        "reason_code": "UNKNOWN",
        "evidence_paths": {},
        "used_files_path": None
    }
    
    # 1. final_audit 읽기
    audit_path = run_dir / "final_audit.json"
    if audit_path.exists():
        try:
            with open(audit_path, 'r', encoding='utf-8') as f:
                audit = json.load(f)
                entry["expected_missions"] = audit.get("expected_missions", 0)
                entry["done_missions"] = audit.get("done_missions", 0)
                entry["api_error_count"] = audit.get("api_error_count", 0)
                entry["exitcode"] = audit.get("exitcode", 999)
                entry["pass_bool"] = audit.get("pass", False)
                entry["reason_code"] = audit.get("reason_code", "UNKNOWN")
        except:
            pass
    
    # 2. blackbox에서 시간 정보
    blackbox_path = run_dir / "blackbox_log.jsonl"
    if blackbox_path.exists():
        try:
            with open(blackbox_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    first = json.loads(lines[0])
                    last = json.loads(lines[-1])
                    entry["start_time"] = first.get("timestamp")
                    entry["end_time"] = last.get("timestamp")
                    
                    # duration 계산
                    try:
                        start_dt = datetime.fromisoformat(entry["start_time"])
                        end_dt = datetime.fromisoformat(entry["end_time"])
                        entry["duration_sec"] = int((end_dt - start_dt).total_seconds())
                    except:
                        pass
        except:
            pass
    
    # 3. 증거 파일 경로
    evidence_files = [
        "verify_report.json",
        "final_audit.json",
        "stamp_manifest.json",
        "stdout_manager.txt",
        "stderr_manager.txt",
        "exitcode.txt"
    ]
    
    for ef in evidence_files:
        fp = run_dir / ef
        entry["evidence_paths"][ef] = str(fp) if fp.exists() else None
    
    # 4. used_files 경로
    used_files_path = run_dir / "run_files_used.json"
    if used_files_path.exists():
        entry["used_files_path"] = str(used_files_path)
    
    return entry


def format_devlog_txt(entry):
    """devlog를 사람이 읽는 txt로 포맷"""
    lines = []
    lines.append("=" * 70)
    lines.append(f"RUN: {entry['run_id']}")
    lines.append("=" * 70)
    lines.append(f"Timestamp: {entry['timestamp']}")
    lines.append(f"Start: {entry['start_time']}")
    lines.append(f"End: {entry['end_time']}")
    lines.append(f"Duration: {entry['duration_sec']} sec")
    lines.append("")
    lines.append(f"Order Path: {entry['order_path']}")
    lines.append(f"Expected Missions: {entry['expected_missions']}")
    lines.append(f"Done Missions: {entry['done_missions']}")
    lines.append(f"API Error Count: {entry['api_error_count']}")
    lines.append("")
    lines.append(f"Exitcode: {entry['exitcode']}")
    lines.append(f"PASS: {entry['pass_bool']}")
    lines.append(f"Reason: {entry['reason_code']}")
    lines.append("")
    lines.append("Evidence Files:")
    for name, path in entry['evidence_paths'].items():
        status = "EXISTS" if path else "MISSING"
        lines.append(f"  {name}: {status}")
    lines.append("")
    
    if entry['used_files_path']:
        lines.append(f"Used Files: {entry['used_files_path']}")
    lines.append("")
    lines.append("=" * 70)
    lines.append("")
    
    return "\n".join(lines)


def append_devlog(run_path, ssot_root):
    """devlog 생성 + 추가"""
    run_dir = Path(run_path)
    root = Path(ssot_root)
    
    # 1. devlog 엔트리 생성
    entry = generate_devlog_entry(run_path, ssot_root)
    if not entry:
        print(f"[ERROR] Could not generate devlog for {run_path}")
        return False
    
    # 2. RUN 폴더에 저장
    entry_json_path = run_dir / "devlog_entry.json"
    with open(entry_json_path, 'w', encoding='utf-8') as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)
    
    entry_txt_path = run_dir / "devlog_entry.txt"
    with open(entry_txt_path, 'w', encoding='utf-8') as f:
        f.write(format_devlog_txt(entry))
    
    print(f"[DEVLOG ENTRY] {run_dir.name}")
    print(f"  {entry_json_path}")
    print(f"  {entry_txt_path}")
    
    # 3. 루트 devlog 폴더에 추가
    devlog_dir = root / "devlog"
    devlog_dir.mkdir(exist_ok=True)
    
    # devlog.jsonl (append)
    devlog_jsonl = devlog_dir / "devlog.jsonl"
    with open(devlog_jsonl, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    # devlog_YYYYMMDD.txt (append)
    today = datetime.now().strftime("%Y%m%d")
    devlog_txt = devlog_dir / f"devlog_{today}.txt"
    with open(devlog_txt, 'a', encoding='utf-8') as f:
        f.write(format_devlog_txt(entry))
    
    print(f"[DEVLOG APPEND]")
    print(f"  {devlog_jsonl}")
    print(f"  {devlog_txt}")
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Devlog Generator")
    parser.add_argument("--run_path", help="RUN directory path")
    parser.add_argument("--latest", action="store_true", help="Use latest RUN")
    parser.add_argument("--ssot_root", default=r"C:\g7core\g7_v1", help="SSOT root")
    
    args = parser.parse_args()
    
    root = Path(args.ssot_root)
    if not root.exists():
        print(f"[ERROR] SSOT_ROOT not found: {args.ssot_root}")
        sys.exit(1)
    
    # RUN 경로 결정
    if args.latest:
        runs_dir = root / "runs"
        run_dirs = sorted(runs_dir.glob("RUN_*"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not run_dirs:
            print("[ERROR] No RUN directories found")
            sys.exit(1)
        run_path = run_dirs[0]
    elif args.run_path:
        run_path = Path(args.run_path)
    else:
        print("[ERROR] Specify --run_path or --latest")
        sys.exit(1)
    
    # devlog 생성
    success = append_devlog(run_path, args.ssot_root)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
