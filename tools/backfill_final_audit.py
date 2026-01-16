import json
import os
import sys
from datetime import datetime

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def file_exists(path: str) -> bool:
    return os.path.exists(path)

def count_lines(path: str) -> int:
    if not file_exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)

def count_files(path: str) -> int:
    if not file_exists(path):
        return 0
    total = 0
    for root, _, files in os.walk(path):
        total += len(files)
    return total

def main():
    if len(sys.argv) != 2:
        print("USAGE: python backfill_final_audit.py <RUN_PATH>")
        sys.exit(2)

    run_path = sys.argv[1]
    verify_path = os.path.join(run_path, "verify_report.json")
    exitcode_path = os.path.join(run_path, "exitcode.txt")
    api_receipt_path = os.path.join(run_path, "api_receipt.jsonl")
    blackbox_path = os.path.join(run_path, "blackbox_log.jsonl")
    stamp_path = os.path.join(run_path, "stamp_manifest.json")
    api_raw_path = os.path.join(run_path, "api_raw")
    out_path = os.path.join(run_path, "final_audit.json")

    if not file_exists(verify_path):
        print(f"FAIL: missing verify_report.json: {verify_path}")
        sys.exit(3)

    verify = read_json(verify_path)

    exitcode = None
    if file_exists(exitcode_path):
        try:
            exitcode = int(read_text(exitcode_path).strip())
        except:
            exitcode = None

    audit = {
        "kind": "FINAL_AUDIT_BACKFILL_V1",
        "run_path": run_path,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "evidence": {
            "exitcode": exitcode,
            "api_receipt_lines": count_lines(api_receipt_path),
            "blackbox_lines": count_lines(blackbox_path),
            "stamp_manifest_exists": file_exists(stamp_path),
            "verify_report_exists": True,
            "api_raw_exists": file_exists(api_raw_path),
            "api_raw_file_count": count_files(api_raw_path),
        },
        "verify_summary": {
            # verify_report 구조가 어떻든 최소한 원문을 보존하는 쪽으로
            "keys": list(verify.keys()) if isinstance(verify, dict) else None,
            "raw": verify,
        },
        "verdict": "WARN"  # 최종 PASS는 gate에서 결정
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(audit, f, ensure_ascii=False, indent=2)

    print(f"OK: wrote {out_path}")

if __name__ == "__main__":
    main()
