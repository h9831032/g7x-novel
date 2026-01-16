"""
G7X check_run_pack.py
RUN 폴더 검사 후 PASS/FAIL 출력 + exitcode 반환

사용법:
    python check_run_pack.py <RUN_PATH> [--expected 120]
    python check_run_pack.py --latest [--expected 120]
"""

import sys
import json
import argparse
from pathlib import Path


def find_latest_run(runs_dir: Path) -> Path:
    """가장 최신 RUN 폴더 찾기"""
    runs = list(runs_dir.glob("RUN_*"))
    if not runs:
        return None
    runs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return runs[0]


def check_run(run_path: Path, expected_missions: int) -> tuple:
    """
    RUN 검사
    Returns: (is_pass, details_dict)
    """
    details = {
        "run_path": str(run_path),
        "expected_missions": expected_missions,
        "checks": {}
    }
    
    if not run_path.exists():
        details["error"] = "RUN path does not exist"
        return False, details
    
    # 1. 필수 파일 체크
    required_files = [
        "verify_report.json",
        "stamp_manifest.json",
        "final_audit.json",
        "exitcode.txt",
        "blackbox_log.jsonl",
        "api_receipt.jsonl"
    ]
    
    for f in required_files:
        details["checks"][f] = (run_path / f).exists()
    
    # 2. exitcode 값
    exitcode_path = run_path / "exitcode.txt"
    if exitcode_path.exists():
        ec = exitcode_path.read_text(encoding="utf-8").strip()
        details["exitcode_value"] = ec
        details["checks"]["exitcode_is_0"] = (ec == "0")
    else:
        details["exitcode_value"] = "MISSING"
        details["checks"]["exitcode_is_0"] = False
    
    # 3. receipts 개수
    receipts_dir = run_path / "receipts" / "mission"
    if receipts_dir.exists():
        receipts_count = len(list(receipts_dir.glob("*.json")))
    else:
        receipts_count = 0
    details["receipts_count"] = receipts_count
    details["checks"]["receipts_match"] = (receipts_count == expected_missions)
    
    # 4. api_receipt.jsonl 라인 수
    api_receipt_path = run_path / "api_receipt.jsonl"
    if api_receipt_path.exists():
        with open(api_receipt_path, "r", encoding="utf-8") as f:
            api_lines = sum(1 for line in f if line.strip())
    else:
        api_lines = 0
    details["api_lines"] = api_lines
    details["checks"]["api_lines_match"] = (api_lines == expected_missions)
    
    # 5. final_audit.json pass 값
    audit_path = run_path / "final_audit.json"
    if audit_path.exists():
        try:
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
            details["audit_pass"] = audit.get("pass", False)
            details["audit_reason_code"] = audit.get("reason_code", "UNKNOWN")
            details["audit_done_missions"] = audit.get("done_missions", 0)
            details["audit_api_error_count"] = audit.get("api_error_count", 0)
        except:
            details["audit_pass"] = False
            details["audit_reason_code"] = "PARSE_ERROR"
    else:
        details["audit_pass"] = False
        details["audit_reason_code"] = "MISSING"
    
    details["checks"]["audit_pass"] = details.get("audit_pass", False)
    
    # 6. blackbox 비어있지 않은지
    bb_path = run_path / "blackbox_log.jsonl"
    if bb_path.exists():
        bb_size = bb_path.stat().st_size
        details["blackbox_size"] = bb_size
        details["checks"]["blackbox_not_empty"] = (bb_size > 0)
    else:
        details["blackbox_size"] = 0
        details["checks"]["blackbox_not_empty"] = False
    
    # 최종 판정
    is_pass = all(details["checks"].values())
    details["final_result"] = "PASS" if is_pass else "FAIL"
    
    return is_pass, details


def main():
    parser = argparse.ArgumentParser(description="G7X RUN Pack Checker")
    parser.add_argument("run_path", nargs="?", help="RUN folder path")
    parser.add_argument("--latest", action="store_true", help="Check latest RUN")
    parser.add_argument("--expected", type=int, default=120, help="Expected missions count")
    parser.add_argument("--ssot", default=r"C:\g7core\g7_v1", help="SSOT root")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    ssot_root = Path(args.ssot)
    
    # RUN 경로 결정
    if args.latest:
        run_path = find_latest_run(ssot_root / "runs")
        if not run_path:
            print("[ERROR] No RUN folders found")
            sys.exit(2)
    elif args.run_path:
        run_path = Path(args.run_path)
    else:
        print("Usage: python check_run_pack.py <RUN_PATH> or --latest")
        sys.exit(2)
    
    # 검사 실행
    is_pass, details = check_run(run_path, args.expected)
    
    if args.json:
        print(json.dumps(details, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("G7X RUN PACK CHECK")
        print("=" * 60)
        print(f"RUN: {details['run_path']}")
        print(f"Expected: {details['expected_missions']} missions")
        print()
        
        print("[CHECKS]")
        for check_name, check_result in details.get("checks", {}).items():
            status = "OK" if check_result else "FAIL"
            print(f"  {check_name}: {status}")
        
        print()
        print(f"[VALUES]")
        print(f"  exitcode_value: {details.get('exitcode_value', 'N/A')}")
        print(f"  receipts_count: {details.get('receipts_count', 0)}")
        print(f"  api_lines: {details.get('api_lines', 0)}")
        print(f"  audit_pass: {details.get('audit_pass', False)}")
        print(f"  audit_reason_code: {details.get('audit_reason_code', 'N/A')}")
        print(f"  audit_done_missions: {details.get('audit_done_missions', 0)}")
        print(f"  audit_api_error_count: {details.get('audit_api_error_count', 0)}")
        print(f"  blackbox_size: {details.get('blackbox_size', 0)} bytes")
        
        print()
        print("=" * 60)
        if is_pass:
            print("[FINAL] PASS")
        else:
            print("[FINAL] FAIL")
        print("=" * 60)
    
    sys.exit(0 if is_pass else 1)


if __name__ == "__main__":
    main()
