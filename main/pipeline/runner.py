"""Mission Runner Pipeline (exponential backoff + longer timeout)"""

import json
import time
import random
import traceback
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Tuple


MIN_SLEEP_SEC = 3.0
MAX_SLEEP_SEC = 6.0
BACKOFF_BASE_SEC = 8


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


class BasicEngineAdapter:
    def __init__(self, api_key: str, model: str, timeout: int = 20, max_retry: int = 3):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retry = max_retry

    def _throttle(self) -> None:
        time.sleep(random.uniform(MIN_SLEEP_SEC, MAX_SLEEP_SEC))

    def generate(self, prompt: str) -> Tuple[str, Dict[str, Any], float]:
        import urllib.request
        import urllib.error

        for attempt in range(self.max_retry):
            try:
                self._throttle()
                
                start_time = time.time()

                url = f"https://generativelanguage.googleapis.com/v1beta/{self.model}:generateContent?key={self.api_key}"

                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.0,
                        "maxOutputTokens": 2048,
                    },
                }

                req = urllib.request.Request(
                    url=url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )

                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    data = json.loads(response.read().decode("utf-8", errors="replace"))
                
                latency = time.time() - start_time

                content = ""
                if isinstance(data, dict) and "candidates" in data and data["candidates"]:
                    c0 = data["candidates"][0]
                    if isinstance(c0, dict) and "content" in c0 and isinstance(c0["content"], dict):
                        parts = c0["content"].get("parts", [])
                        if isinstance(parts, list):
                            content = "".join(str(p.get("text", "")) for p in parts)

                return content, {"raw": data}, latency

            except urllib.error.HTTPError as e:
                latency = time.time() - start_time
                body = ""
                try:
                    body = e.read().decode("utf-8", errors="replace")
                except Exception:
                    body = ""
                
                if attempt < self.max_retry - 1:
                    backoff = BACKOFF_BASE_SEC * (2 ** attempt)
                    jitter = random.uniform(0, 2)
                    wait_time = backoff + jitter
                    
                    print(f"[RETRY] HTTPError {e.code}, attempt {attempt + 1}/{self.max_retry}, wait {wait_time:.1f}s")
                    time.sleep(wait_time)
                    continue
                
                raise RuntimeError(f"HTTPError {e.code}: {body}") from e

            except Exception as e:
                latency = time.time() - start_time if 'start_time' in locals() else 0.0
                
                if attempt < self.max_retry - 1:
                    backoff = BACKOFF_BASE_SEC * (2 ** attempt)
                    jitter = random.uniform(0, 2)
                    wait_time = backoff + jitter
                    
                    print(f"[RETRY] {type(e).__name__}, attempt {attempt + 1}/{self.max_retry}, wait {wait_time:.1f}s")
                    time.sleep(wait_time)
                    continue
                
                raise RuntimeError(f"API call failed: {e}") from e

        raise RuntimeError("Max retries exceeded")


def _isolate_to_failbox(
    mission_id: str,
    receipt_data: Dict[str, Any],
    fail_box_missions: Path,
    fail_box_events: Path,
    run_id: str,
) -> None:
    fail_mission_file = fail_box_missions / f"{mission_id}.json"
    with open(fail_mission_file, "w", encoding="utf-8") as f:
        json.dump(receipt_data, f, indent=2, ensure_ascii=False)
    
    event = {
        "run_id": run_id,
        "mission_id": mission_id,
        "timestamp": _now_iso(),
        "status": receipt_data.get("status", "UNKNOWN"),
        "error": receipt_data.get("error", "")[:500],
        "order_prefix": receipt_data.get("original_order", "")[:80],
    }
    
    events_file = fail_box_events / "fail_events.jsonl"
    with open(events_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def run_missions(
    orders: List[str],
    compiler,
    engine: BasicEngineAdapter,
    evidence_writer,
    fail_box_missions: Path,
    fail_box_events: Path,
    max_consecutive_errors: int = 10,
) -> Tuple[int, Dict[str, Any], str]:
    """Mission execution loop with exponential backoff"""
    total = len(orders)
    done = 0
    api_error = 0
    consecutive_errors = 0
    reason_code = "UNKNOWN"
    error_missions = []
    
    run_id = fail_box_missions.parent.parent.name

    print(f"[RUNNER] Starting {total} missions...")

    try:
        for idx, order_line in enumerate(orders, 1):
            mission_id = f"mission_{idx:04d}"

            prompt, meta = compiler.compile_prompt(order_line)
            if not prompt:
                continue

            print(f"[MISSION] {mission_id} | Order: {order_line[:50]}...")
            
            evidence_writer.append_blackbox_event("MISSION_START", {
                "mission_id": mission_id,
                "order": order_line[:80]
            })

            try:
                content, raw_meta, latency = engine.generate(prompt)
                
                evidence_writer.log_api_call(mission_id, "SUCCESS", latency)
                
                receipt_data = {
                    "mission_id": mission_id,
                    "original_order": order_line,
                    "prompt": prompt,
                    "content": content,
                    "status": "SUCCESS",
                    "timestamp": _now_iso(),
                    "meta": meta,
                    "raw": raw_meta,
                }
                evidence_writer.write_receipt(mission_id, receipt_data)
                
                evidence_writer.append_blackbox_event("MISSION_SUCCESS", {
                    "mission_id": mission_id
                })
                
                done += 1
                consecutive_errors = 0
                print(f"[MISSION] {mission_id} status: SUCCESS")

            except Exception as e:
                api_error += 1
                consecutive_errors += 1
                error_missions.append(mission_id)
                
                evidence_writer.log_api_call(mission_id, "API_ERROR", 0.0, str(e))
                
                receipt_data = {
                    "mission_id": mission_id,
                    "original_order": order_line,
                    "prompt": prompt,
                    "content": "",
                    "status": "API_ERROR",
                    "error": str(e),
                    "timestamp": _now_iso(),
                    "meta": meta,
                }
                evidence_writer.write_receipt(mission_id, receipt_data)
                
                evidence_writer.append_blackbox_event("MISSION_FAIL", {
                    "mission_id": mission_id,
                    "error": str(e)[:200]
                })
                
                _isolate_to_failbox(
                    mission_id,
                    receipt_data,
                    fail_box_missions,
                    fail_box_events,
                    run_id,
                )
                
                print(f"[MISSION] {mission_id} status: API_ERROR - {e}")

                if consecutive_errors >= max_consecutive_errors:
                    print(f"[FAIL_FAST] Consecutive errors >= {max_consecutive_errors}")
                    reason_code = "API_STALL"
                    break

                if api_error >= 20:
                    print(f"[FAIL_FAST] Total errors >= 20")
                    reason_code = "API_OVERLOAD"
                    break

    except KeyboardInterrupt:
        print("\n[RUNNER] Interrupted by user")
        reason_code = "INTERRUPTED"
        raise

    if reason_code == "UNKNOWN":
        if done == total and api_error == 0:
            reason_code = "ORDER_EOF"
        elif api_error > 0:
            reason_code = "PARTIAL_COMPLETION"

    print(f"[RUNNER] Completed: {done}/{total} missions, API errors: {api_error}")

    exitcode = 0
    if done != total or api_error > 0:
        exitcode = 1

    stats = {
        "expected_missions": total,
        "done_missions": done,
        "api_error_count": api_error,
        "error_missions": error_missions,
    }

    return exitcode, stats, reason_code


def run_orders(mission_orders: List[str]) -> Dict[str, Any]:
    """
    mission_orders를 받아 순차 실행 (최소 구현, 베이직엔진 용접 준비)

    Args:
        mission_orders: 미션 목록

    Returns:
        Dict[str, Any]: 실행 결과 요약
    """
    total = len(mission_orders)
    done = 0
    errors = 0

    print(f"[run_orders] Starting {total} missions...")

    for idx, order in enumerate(mission_orders, 1):
        mission_id = f"mission_{idx:04d}"
        print(f"[{mission_id}] {order[:50]}...")

        # 실제 실행 로직은 추후 베이직엔진과 용접
        # 현재는 플레이스홀더
        done += 1

    print(f"[run_orders] Completed: {done}/{total} missions")

    return {
        "total": total,
        "done": done,
        "errors": errors,
    }
