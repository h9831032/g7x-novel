"""
G7X Latest RUN Summarizer v1
- 최신 RUN_PATH 찾기
- 성공/실패 수 요약
- evidence 파일 목록 출력
- devlog 생성 여부 확인
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    ssot_root = Path(r"C:\g7core\g7_v1")
    runs_dir = ssot_root / "runs"

    if not runs_dir.exists():
        print("[ERROR] runs directory not found")
        return 1

    # 최신 RUN 폴더 찾기
    run_folders = sorted(runs_dir.glob("RUN_*"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not run_folders:
        print("[ERROR] No RUN folders found")
        return 1

    latest_run = run_folders[0]
    print(f"[RUN_PATH] {latest_run}")
    print("")

    # verify_report.json 읽기
    verify_report = latest_run / "verify_report.json"
    if verify_report.exists():
        with open(verify_report, "r", encoding="utf-8") as f:
            report = json.load(f)

        print("[SUMMARY]")
        print(f"  exitcode: {report.get('exitcode', '?')}")
        print(f"  expected_missions: {report.get('expected_missions', '?')}")
        print(f"  done_missions: {report.get('done_missions', '?')}")
        print(f"  api_error_count: {report.get('api_error_count', '?')}")
        print(f"  reason_code: {report.get('reason_code', '?')}")
    else:
        print("[WARN] verify_report.json not found")

    print("")

    # evidence 파일 목록
    evidence_files = [
        "verify_report.json",
        "budget_guard.log",
        "stdout_manager.txt",
        "stderr_manager.txt",
    ]

    print("[EVIDENCE FILES]")
    for fname in evidence_files:
        fpath = latest_run / fname
        if fpath.exists():
            size = fpath.stat().st_size
            print(f"  ✓ {fname} ({size:,} bytes)")
        else:
            print(f"  ✗ {fname} (MISSING)")

    print("")

    # devlog 확인
    devlog_file = ssot_root / "DEVLOG" / "devlog_runs.jsonl"
    if devlog_file.exists():
        print(f"[DEVLOG] ✓ {devlog_file}")

        # 마지막 라인 읽기
        with open(devlog_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                last_entry = json.loads(lines[-1])
                print(f"  Latest entry: run_id={last_entry.get('run_id')}, pass={last_entry.get('pass')}")
    else:
        print("[DEVLOG] ✗ devlog_runs.jsonl not found")

    print("")
    print("[DONE]")
    return 0

if __name__ == "__main__":
    sys.exit(main())
