"""
G7X RUN File Scanner
이번 RUN에서 실제 사용/수정된 파일 추출
"""

import os
import sys
import json
import glob
from pathlib import Path
from datetime import datetime


def scan_run_files(run_path, ssot_root):
    """RUN에서 사용된 파일 스캔"""
    run_dir = Path(run_path)
    root = Path(ssot_root)
    
    if not run_dir.exists():
        return {"error": f"RUN path not found: {run_path}"}
    
    result = {
        "run_id": run_dir.name,
        "run_path": str(run_dir),
        "scan_time": datetime.now().isoformat(),
        "core_files": [],
        "modified_files": [],
        "evidence_files": []
    }
    
    # 1. 핵심 파일 (항상 포함)
    core_files = [
        "main/manager.py",
        "engine/evidence_writer.py",
        "tools/check_run_pack.py",
        "tools/generate_devlog.py",
        "tools/make_integration_map.py",
        "tools/scan_run_files.py",
        "main/night_shift_guard_v5.py"
    ]
    
    for cf in core_files:
        fp = root / cf
        if fp.exists():
            result["core_files"].append({
                "path": cf,
                "size": fp.stat().st_size,
                "mtime": datetime.fromtimestamp(fp.stat().st_mtime).isoformat()
            })
    
    # 2. RUN 시작/종료 시간 추정
    try:
        blackbox_path = run_dir / "blackbox_log.jsonl"
        if blackbox_path.exists():
            with open(blackbox_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    first = json.loads(lines[0])
                    last = json.loads(lines[-1])
                    run_start = datetime.fromisoformat(first.get("timestamp", ""))
                    run_end = datetime.fromisoformat(last.get("timestamp", ""))
                    
                    # RUN 기간 동안 수정된 파일 찾기
                    for pattern in ["**/*.py", "**/*.ps1", "**/*.txt"]:
                        for fp in root.glob(pattern):
                            if "runs" in str(fp) or "venv" in str(fp) or ".git" in str(fp):
                                continue
                            
                            try:
                                mtime = datetime.fromtimestamp(fp.stat().st_mtime)
                                if run_start <= mtime <= run_end + datetime.timedelta(minutes=5):
                                    rel_path = fp.relative_to(root)
                                    result["modified_files"].append({
                                        "path": str(rel_path),
                                        "size": fp.stat().st_size,
                                        "mtime": mtime.isoformat()
                                    })
                            except:
                                pass
                    
                    # 최대 50개로 제한
                    result["modified_files"] = sorted(
                        result["modified_files"],
                        key=lambda x: x["mtime"],
                        reverse=True
                    )[:50]
    except:
        pass
    
    # 3. 증거 파일
    evidence_files = [
        "verify_report.json",
        "stamp_manifest.json",
        "final_audit.json",
        "exitcode.txt",
        "blackbox_log.jsonl",
        "api_receipt.jsonl",
        "stdout_manager.txt",
        "stderr_manager.txt"
    ]
    
    for ef in evidence_files:
        fp = run_dir / ef
        if fp.exists():
            result["evidence_files"].append({
                "name": ef,
                "size": fp.stat().st_size
            })
    
    return result


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="RUN File Scanner")
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
    
    # 스캔 실행
    result = scan_run_files(run_path, args.ssot_root)
    
    # 저장 (RUN 폴더 내부)
    output_run = Path(run_path) / "run_files_used.json"
    with open(output_run, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"[SCAN] {result['run_id']}")
    print(f"  Core files: {len(result['core_files'])}")
    print(f"  Modified files: {len(result['modified_files'])}")
    print(f"  Evidence files: {len(result['evidence_files'])}")
    
    # 저장 (logs 폴더)
    logs_dir = root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    output_logs = logs_dir / f"run_files_used_{result['run_id']}.json"
    with open(output_logs, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SAVED]")
    print(f"  {output_run}")
    print(f"  {output_logs}")


if __name__ == "__main__":
    main()
