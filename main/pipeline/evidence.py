"""Evidence Writer Pipeline (full evidence layer)"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Any, Dict


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


class EvidenceWriter:
    def __init__(self, run_path: Path):
        self.run_path = Path(run_path)
        self.receipts_dir = self.run_path / "receipts" / "mission"
        self.receipts_dir.mkdir(parents=True, exist_ok=True)
        
        self.blackbox_path = self.run_path / "blackbox_log.jsonl"
        self.api_receipt_path = self.run_path / "api_receipt.jsonl"
        
        self._append_blackbox_event("RUN_START", {"run_id": self.run_path.name})

    def append_blackbox_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Append event to blackbox log"""
        event = {
            "timestamp": _now_iso(),
            "event": event_type,
            "data": data
        }
        with open(self.blackbox_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    
    def _append_blackbox_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Internal blackbox append"""
        self.append_blackbox_event(event_type, data)

    def log_api_call(self, mission_id: str, status: str, latency: float, error: str = "") -> None:
        """Log API call to api_receipt.jsonl"""
        record = {
            "mission_id": mission_id,
            "timestamp": _now_iso(),
            "status": status,
            "latency_sec": round(latency, 2),
            "error": error[:200] if error else ""
        }
        with open(self.api_receipt_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def write_receipt(self, mission_id: str, data: Dict[str, Any]) -> None:
        receipt_file = self.receipts_dir / f"{mission_id}.json"
        with open(receipt_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def finalize(self, exitcode: int, stats: Dict[str, Any]) -> None:
        exitcode_file = self.run_path / "exitcode.txt"
        exitcode_file.write_text(str(exitcode), encoding="utf-8")

        verify_report = {
            "run_id": self.run_path.name,
            "exitcode": exitcode,
            "timestamp": _now_iso(),
            "pass": (exitcode == 0),
            "fail_box_count": stats.get("fail_box_count", 0),
            "api_error_count": stats.get("api_error_count", 0),
            "done_success": stats.get("done_missions", 0),
            **stats,
        }

        verify_path = self.run_path / "verify_report.json"
        with open(verify_path, "w", encoding="utf-8") as f:
            json.dump(verify_report, f, indent=2, ensure_ascii=False)

        audit = {
            "run_id": self.run_path.name,
            "timestamp": _now_iso(),
            "pass": (exitcode == 0),
            "exitcode": exitcode,
            "reason_code": stats.get("reason_code", "UNKNOWN"),
            "receipts_count": len(list(self.receipts_dir.glob("*.json"))),
            "fail_box_count": stats.get("fail_box_count", 0),
            "api_error_count": stats.get("api_error_count", 0),
            "done_missions": stats.get("done_missions", 0),
        }

        audit_path = self.run_path / "final_audit.json"
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(audit, f, indent=2, ensure_ascii=False)
        
        self._write_stamp_manifest(stats)
        
        self._append_blackbox_event("RUN_END", {
            "exitcode": exitcode,
            "reason_code": stats.get("reason_code", "UNKNOWN")
        })

    def _write_stamp_manifest(self, stats: Dict[str, Any]) -> None:
        """Write stamp manifest for run seal"""
        receipts = list(self.receipts_dir.glob("*.json"))
        
        receipt_hash = hashlib.sha256()
        for receipt in sorted(receipts):
            receipt_hash.update(receipt.read_bytes())
        
        api_lines = 0
        if self.api_receipt_path.exists():
            with open(self.api_receipt_path, "r", encoding="utf-8") as f:
                api_lines = sum(1 for line in f if line.strip())
        
        manifest = {
            "run_id": self.run_path.name,
            "timestamp": _now_iso(),
            "total_missions": stats.get("expected_missions", 0),
            "api_call_count": api_lines,
            "fail_count": stats.get("api_error_count", 0),
            "receipts_hash": receipt_hash.hexdigest()[:16],
        }
        
        manifest_path = self.run_path / "stamp_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
