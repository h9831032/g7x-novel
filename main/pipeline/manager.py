"""
G7X Manager - Main Entry Point
CLI + Flow + Finalize + Devlog
FAIL_BOX auto-isolation for failed missions
"""

import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))
from devlog_writer import generate_devlog_5files
from datetime import datetime
import argparse

sys.path.insert(0, str(Path(__file__).parent / "pipeline"))
from catalog import CatalogCompiler
from evidence import EvidenceWriter
from runner import BasicEngineAdapter, run_missions
from devlog import call_devlog_generator, write_daily_devlog
from retry_order import generate_retry_order


GEMINI_API_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
DEFAULT_MODEL = "models/gemini-2.0-flash"

MAX_CONSECUTIVE_ERRORS = 10
MAX_RETRY_PER_MISSION = 3
API_TIMEOUT_SEC = 13


class RunManager:
    def __init__(self, ssot_root: Path):
        self.ssot_root = Path(ssot_root)
        self.runs_dir = self.ssot_root / "runs"
        self.runs_dir.mkdir(exist_ok=True)

        run_id = datetime.now().strftime("RUN_%Y%m%d_%H%M%S_%f")[:26]
        self.run_path = self.runs_dir / run_id

        try:
            self.run_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"[FAIL_FAST] Cannot create run_path: {e}", file=sys.stderr)
            sys.stderr.flush()
            sys.exit(1)

        print(f"[MANAGER] RUN CREATED: {self.run_path}")
        print(f"TARGET_RUN_PATH:{self.run_path}")
        sys.stdout.flush()

        if not self.run_path.exists():
            print(f"[FAIL_FAST] run_path not found after creation", file=sys.stderr)
            sys.stderr.flush()
            sys.exit(1)

        self.fail_box_missions = self.run_path / "FAIL_BOX" / "missions"
        self.fail_box_events = self.run_path / "FAIL_BOX" / "events"
        self.fail_box_missions.mkdir(parents=True, exist_ok=True)
        self.fail_box_events.mkdir(parents=True, exist_ok=True)

        self.evidence = EvidenceWriter(self.run_path)
        self.engine = BasicEngineAdapter(
            GEMINI_API_KEY, 
            DEFAULT_MODEL,
            timeout=API_TIMEOUT_SEC,
            max_retry=MAX_RETRY_PER_MISSION
        )
        self.compiler = CatalogCompiler(self.ssot_root)

        print(f"[MANAGER] Engine initialized: {DEFAULT_MODEL}")

    def load_orders(self, order_path: Path):
        if not order_path.exists():
            raise FileNotFoundError(f"Order file not found: {order_path}")

        with open(order_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f"[MANAGER] Loaded {len(lines)} orders from {order_path}")
        return lines

    def run(self, order_path: Path) -> int:
        self.order_path = order_path
        exitcode = 0
        reason_code = "UNKNOWN"
        stats = {
            "expected_missions": 0,
            "done_missions": 0,
            "api_error_count": 0,
            "error_missions": [],
        }

        try:
            orders = self.load_orders(order_path)
            self.compiler.load_catalog(order_path)

            stats["expected_missions"] = len(orders)

            exitcode, run_stats, reason_code = run_missions(
                orders,
                self.compiler,
                self.engine,
                self.evidence,
                self.fail_box_missions,
                self.fail_box_events,
                max_consecutive_errors=MAX_CONSECUTIVE_ERRORS,
            )
            
            stats.update(run_stats)

        except KeyboardInterrupt:
            print("\n[INTERRUPTED] Ctrl+C detected - finalizing...")
            exitcode = 1
            reason_code = "INTERRUPTED"

        except Exception as e:
            print(f"[FATAL] Run failed: {e}")
            traceback.print_exc()
            exitcode = 2
            reason_code = "FATAL_ERROR"

        finally:
            stats["reason_code"] = reason_code
            
            fail_box_count = len(list(self.fail_box_missions.glob("*.json")))
            stats["fail_box_count"] = fail_box_count
            
            self.evidence.finalize(exitcode, stats)

            self._write_summary(stats, exitcode, reason_code)

            write_daily_devlog(self.run_path, stats, reason_code)

            generate_retry_order(self.run_path, self.ssot_root, self.order_path)

            try:
                call_devlog_generator(self.run_path, self.ssot_root)
            except Exception as e:
                print(f"[WARN] devlog generation failed: {e}")

            print(f"[MANAGER] RUN COMPLETE: exitcode={exitcode}, reason={reason_code}")
            sys.stdout.flush()
            sys.stderr.flush()

        return exitcode

    def _write_summary(self, stats, exitcode, reason_code):
        import json
        
        error_missions = stats.get("error_missions", [])
        
        summary = {
            "run_id": self.run_path.name,
            "timestamp": datetime.now().isoformat(),
            "exitcode": exitcode,
            "reason_code": reason_code,
            "expected_missions": stats.get("expected_missions", 0),
            "done_success": stats.get("done_missions", 0),
            "api_error_count": stats.get("api_error_count", 0),
            "fail_box_count": stats.get("fail_box_count", 0),
            "error_missions": error_missions,
            "first_error_mission_id": error_missions[0] if error_missions else None,
            "last_error_mission_id": error_missions[-1] if error_missions else None,
        }
        
        summary_path = self.run_path / "run_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="G7X Manager")
    parser.add_argument("--order_path", required=True, help="Order file path")
    parser.add_argument("--ssot_root", default=r"C:\g7core\g7_v1", help="SSOT root")

    args = parser.parse_args()

    ssot_root = Path(args.ssot_root)
    if not ssot_root.exists():
        print(f"[ERROR] SSOT_ROOT not found: {ssot_root}")
        sys.exit(1)

    order_path = Path(args.order_path)
    if not order_path.is_absolute():
        order_str = str(order_path).replace("\\", "/")

        if "GPTORDER" in order_str:
            order_path = ssot_root / order_path
        else:
            order_path = ssot_root / "GPTORDER" / args.order_path

    try:
        manager = RunManager(ssot_root)
        exitcode = manager.run(order_path)

        sys.stdout.flush()
        sys.stderr.flush()

        
        try:
            devlog_files = generate_devlog_5files(self.ssot_root)
            print("[DEVLOG] Auto-generated 5 files")
        except Exception as e:
            print(f"[DEVLOG ERROR] {e}")
            exitcode = 1

        sys.exit(exitcode)
    except Exception as e:
        print(f"[FATAL] Manager failed to start: {e}")
        traceback.print_exc()

        sys.stdout.flush()
        sys.stderr.flush()

        sys.exit(1)


if __name__ == "__main__":
    main()