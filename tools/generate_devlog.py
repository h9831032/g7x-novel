"""
G7X DEVLOG Generator (v3.4)
- append_devlog(): RUN 결과를 devlog.jsonl에 추가
- 증거팩 기반으로 자동 생성
- manager.py에서 호출됨
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


def append_devlog(run_path: Path, ssot_root: Path) -> bool:
    """
    RUN 결과를 devlog.jsonl에 추가
    
    Args:
        run_path: RUN 폴더 경로 (예: C:\g7core\g7_v1\runs\RUN_20260117_...)
        ssot_root: SSOT 루트 경로 (예: C:\g7core\g7_v1)
    
    Returns:
        성공 여부
    """
    run_path = Path(run_path)
    ssot_root = Path(ssot_root)
    
    devlog_path = ssot_root / "devlog.jsonl"
    
    try:
        # 1. final_audit.json 읽기
        audit_path = run_path / "final_audit.json"
        if not audit_path.exists():
            print(f"[DEVLOG ERROR] final_audit.json not found: {audit_path}")
            return False
        
        with open(audit_path, "r", encoding="utf-8") as f:
            audit = json.load(f)
        
        # 2. verify_report.json 읽기 (옵션)
        verify_path = run_path / "verify_report.json"
        verify_data = {}
        if verify_path.exists():
            with open(verify_path, "r", encoding="utf-8") as f:
                verify_data = json.load(f)
        
        # 3. DEVLOG 엔트리 생성
        entry = {
            "timestamp": datetime.now().isoformat(),
            "run_id": audit.get("run_id", run_path.name),
            "run_path": str(run_path),
            "pass": audit.get("pass", False),
            "exitcode": audit.get("exitcode", -1),
            "expected_missions": audit.get("expected_missions", 0),
            "done_missions": audit.get("done_missions", 0),
            "api_error_count": audit.get("api_error_count", 0),
            "reason_code": audit.get("reason_code", "UNKNOWN"),
            "receipts_count": audit.get("receipts_count", 0),
            "api_lines": audit.get("api_receipt_lines", 0),
            "pass_conditions": audit.get("pass_conditions", {}),
        }
        
        # 4. devlog.jsonl에 추가
        with open(devlog_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        print(f"[DEVLOG] Entry appended: {entry['run_id']} (pass={entry['pass']})")
        return True
        
    except Exception as e:
        print(f"[DEVLOG ERROR] Failed to append: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_devlog_summary(ssot_root: Path, last_n: int = 10) -> list:
    """
    최근 N개의 devlog 엔트리 반환
    """
    devlog_path = Path(ssot_root) / "devlog.jsonl"
    
    if not devlog_path.exists():
        return []
    
    entries = []
    with open(devlog_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    return entries[-last_n:]


if __name__ == "__main__":
    # 테스트용 CLI
    import argparse
    
    parser = argparse.ArgumentParser(description="G7X DEVLOG Generator")
    parser.add_argument("--run_path", required=True, help="RUN folder path")
    parser.add_argument("--ssot_root", default="C:\\g7core\\g7_v1", help="SSOT root path")
    
    args = parser.parse_args()
    
    success = append_devlog(Path(args.run_path), Path(args.ssot_root))
    print(f"Result: {'SUCCESS' if success else 'FAIL'}")
