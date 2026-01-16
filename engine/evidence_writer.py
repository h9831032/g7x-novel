"""
G7X Evidence Writer (거짓합격 제거 버전)
- [FIX 2026-01-12] expected_missions 기반 엄격 검증
- pass = (exitcode==0) AND (done==expected) AND (receipts==expected) AND (api_lines==expected) AND (api_error==0)
- reason_code 기록 추가
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class EvidenceWriter:
    """RUN 폴더 증거팩 작성 전용"""
    
    def __init__(self, run_path: Path):
        self.run_path = Path(run_path)
        self.blackbox_path = self.run_path / "blackbox_log.jsonl"
        self.receipts_dir = self.run_path / "receipts" / "mission"
        self.api_receipt_path = self.run_path / "api_receipt.jsonl"
        self.api_raw_dir = self.run_path / "api_raw"
        
        # 필수 디렉터리 생성
        self.receipts_dir.mkdir(parents=True, exist_ok=True)
        self.api_raw_dir.mkdir(parents=True, exist_ok=True)
        
        # 블랙박스 시작 이벤트
        self._write_blackbox_event("START", {"run_id": self.run_path.name})
    
    def _write_blackbox_event(self, event_type: str, data: Dict[str, Any]):
        """블랙박스 이벤트 기록 (append only)"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "data": data
        }
        with open(self.blackbox_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    
    def write_mission_receipt(self, mission_id: str, mission_data: Dict[str, Any]):
        """
        미션 영수증 개별 파일 생성
        """
        receipt_file = self.receipts_dir / f"{mission_id}.json"
        
        receipt = {
            "mission_id": mission_id,
            "timestamp": datetime.now().isoformat(),
            "status": mission_data.get("status", "UNKNOWN"),
            "content_hash": self._calculate_hash(mission_data),
            "metadata": mission_data
        }
        
        # 실제 파일 write
        with open(receipt_file, "w", encoding="utf-8") as f:
            json.dump(receipt, indent=2, ensure_ascii=False, fp=f)
        
        # API 영수증 로그 추가
        with open(self.api_receipt_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "mission_id": mission_id,
                "timestamp": receipt["timestamp"],
                "status": receipt["status"],
                "hash": receipt["content_hash"]
            }, ensure_ascii=False) + "\n")
        
        # 블랙박스 진행 기록
        self._write_blackbox_event("PROGRESS", {
            "mission_id": mission_id,
            "status": receipt["status"]
        })
    
    def finalize(
        self,
        exitcode: int,
        expected_missions: int,
        done_missions: int,
        api_error_count: int,
        reason_code: str
    ):
        """
        실행 종료 시 최종 증거팩 생성
        [FIX] expected_missions 기반 엄격 검증
        """
        
        # 1. 영수증 카운트
        receipts_list = list(self.receipts_dir.glob("*.json"))
        receipts_count = len(receipts_list)
        receipts_nonempty_count = sum(1 for p in receipts_list if p.stat().st_size > 0)
        
        # 2. API 영수증 라인 수
        api_lines = self._count_lines(self.api_receipt_path)
        
        # 3. api_raw 파일 수
        api_raw_count = len(list(self.api_raw_dir.glob("*.json"))) if self.api_raw_dir.exists() else 0
        
        # ============================================
        # [FIX] 엄격한 PASS 조건 (== 비교, >= 아님!)
        # ============================================
        # STRICT PASS RULE (G7X Constitution):
        # 1. exitcode == 0 (정상 종료)
        # 2. expected_missions > 0 (주문이 0개면 무조건 FAIL)
        # 3. done_missions == expected_missions (정확히 일치)
        # 4. receipts_count == expected_missions (영수증 개수 일치)
        # 5. receipts_nonempty_count == expected_missions (빈 영수증 금지)
        # 6. api_receipt_lines == expected_missions (API 로그 라인 수 일치)
        # 7. api_error_count == 0 (API 에러 0개)
        #
        # Helper signature for external use:
        # def is_strict_pass(run_summary: dict) -> bool:
        #     return (
        #         run_summary.get("exitcode") == 0
        #         and run_summary.get("expected_missions", 0) > 0
        #         and run_summary.get("done_missions") == run_summary.get("expected_missions")
        #         and run_summary.get("api_error_count", 0) == 0
        #     )
        # ============================================
        
        is_pass = (
            exitcode == 0
            and expected_missions > 0  # 주문이 0개면 무조건 FAIL
            and done_missions == expected_missions
            and receipts_count == expected_missions
            and receipts_nonempty_count == expected_missions
            and api_lines == expected_missions
            and api_error_count == 0
        )
        
        # PASS가 아닌데 exitcode가 0이면 강제로 1로 변경
        if not is_pass and exitcode == 0:
            exitcode = 1
            if reason_code == "ORDER_EOF":
                reason_code = "PASS_CHECK_FAILED"
        
        # 4. exitcode.txt 생성
        exitcode_path = self.run_path / "exitcode.txt"
        exitcode_path.write_text(str(exitcode), encoding="utf-8")
        
        # 5. stamp_manifest.json 생성
        stamp_manifest = {
            "run_id": self.run_path.name,
            "timestamp": datetime.now().isoformat(),
            "files": {}
        }
        
        for file_path in self.run_path.rglob("*"):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(self.run_path))
                stamp_manifest["files"][rel_path] = {
                    "size": file_path.stat().st_size,
                    "sha1": self._file_hash(file_path)
                }
        
        stamp_path = self.run_path / "stamp_manifest.json"
        with open(stamp_path, "w", encoding="utf-8") as f:
            json.dump(stamp_manifest, f, indent=2, ensure_ascii=False)
        
        # 6. verify_report.json 생성
        verify_report = {
            "run_id": self.run_path.name,
            "timestamp": datetime.now().isoformat(),
            "exitcode": exitcode,
            "expected_missions": expected_missions,
            "done_missions": done_missions,
            "receipts_count": receipts_count,
            "receipts_nonempty_count": receipts_nonempty_count,
            "api_receipt_lines": api_lines,
            "api_raw_count": api_raw_count,
            "api_error_count": api_error_count,
            "pass": is_pass,
            "reason_code": reason_code,
            "required_files": {
                "verify_report.json": True,
                "stamp_manifest.json": stamp_path.exists(),
                "final_audit.json": False,  # 아직
                "exitcode.txt": exitcode_path.exists(),
                "blackbox_log.jsonl": self.blackbox_path.exists(),
                "api_receipt.jsonl": self.api_receipt_path.exists()
            }
        }
        
        verify_path = self.run_path / "verify_report.json"
        with open(verify_path, "w", encoding="utf-8") as f:
            json.dump(verify_report, f, indent=2, ensure_ascii=False)
        
        # 7. final_audit.json 생성
        final_audit = {
            "run_id": self.run_path.name,
            "timestamp": datetime.now().isoformat(),
            "pass": is_pass,
            "exitcode": exitcode,
            "expected_missions": expected_missions,
            "done_missions": done_missions,
            "receipts_count": receipts_count,
            "receipts_nonempty_count": receipts_nonempty_count,
            "api_receipt_lines": api_lines,
            "api_raw_count": api_raw_count,
            "api_error_count": api_error_count,
            "reason_code": reason_code,
            "pass_conditions": {
                "exitcode_is_0": exitcode == 0,
                "expected_gt_0": expected_missions > 0,
                "done_eq_expected": done_missions == expected_missions,
                "receipts_eq_expected": receipts_count == expected_missions,
                "receipts_nonempty_eq_expected": receipts_nonempty_count == expected_missions,
                "api_lines_eq_expected": api_lines == expected_missions,
                "api_error_is_0": api_error_count == 0
            },
            "missing_required_files": [
                name for name, exists in verify_report["required_files"].items()
                if not exists
            ]
        }
        
        audit_path = self.run_path / "final_audit.json"
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(final_audit, f, indent=2, ensure_ascii=False)
        
        # verify_report 재작성 (final_audit 존재 반영)
        verify_report["required_files"]["final_audit.json"] = audit_path.exists()
        with open(verify_path, "w", encoding="utf-8") as f:
            json.dump(verify_report, f, indent=2, ensure_ascii=False)
        
        # 8. 블랙박스 종료 이벤트
        self._write_blackbox_event("END", {
            "exitcode": exitcode,
            "expected_missions": expected_missions,
            "done_missions": done_missions,
            "receipts_count": receipts_count,
            "receipts_nonempty_count": receipts_nonempty_count,
            "api_lines": api_lines,
            "api_error_count": api_error_count,
            "reason_code": reason_code,
            "pass": is_pass
        })
    
    def _calculate_hash(self, data: Any) -> str:
        """데이터 해시 계산"""
        content = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha1(content.encode()).hexdigest()
    
    def _file_hash(self, file_path: Path) -> str:
        """파일 SHA1 해시"""
        sha1 = hashlib.sha1()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha1.update(chunk)
        return sha1.hexdigest()
    
    def _count_lines(self, file_path: Path) -> int:
        """파일 라인 수 카운트"""
        if not file_path.exists():
            return 0
        with open(file_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
