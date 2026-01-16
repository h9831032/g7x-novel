"""
G7X Night Shift Guard v5.1
- [FIX] 새 RUN 감지: len==1 조건 제거, 가장 최신 RUN 선택
- [FIX] verify_run: 동적 expected_missions (주문서 줄 수 기준)
- [FIX] TARGET_RUN_PATH 파싱 지원 (manager stdout에서 추출)
"""

from __future__ import annotations
import argparse, glob, os, subprocess, sys, time, json, re
from pathlib import Path

ROOT = Path(r"C:\g7core\g7_v1")
RUNS_DIR = ROOT / "runs"
MANAGER = ROOT / "main" / "manager.py"

BAN_TOKENS = [
    "time.sleep(",
    "while true",
    "simulate",
    "mock",
    "dummy",
]

def gate_A_static_scan() -> None:
    targets = [
        ROOT / "main" / "manager.py",
        ROOT / "tools" / "one_shot_night_work_600.py",
    ]
    for p in targets:
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8", errors="ignore").lower()
        hits = [t for t in BAN_TOKENS if t.lower() in s]
        if hits:
            print("[GATE_A_FAIL]", str(p), hits)
            sys.exit(1)

def list_runs() -> set[str]:
    if not RUNS_DIR.exists():
        return set()
    return set(glob.glob(str(RUNS_DIR / "RUN_*")))

def make_guard_fail_run() -> Path:
    ts = time.strftime("%Y%m%d_%H%M%S")
    p = RUNS_DIR / f"RUN_GUARD_FAIL_{ts}"
    p.mkdir(parents=True, exist_ok=True)
    return p

def ensure_exitcode(run_dir: Path, code: int) -> None:
    (run_dir / "exitcode.txt").write_text(str(code), encoding="utf-8")

def append_blackbox(run_dir: Path, obj: dict) -> None:
    bb = run_dir / "blackbox_log.jsonl"
    with bb.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def parse_target_run_path(stdout: str) -> str:
    """
    manager stdout에서 TARGET_RUN_PATH: 추출
    """
    for line in stdout.splitlines():
        if line.startswith("TARGET_RUN_PATH:"):
            return line.split(":", 1)[1].strip()
    return ""

def run_manager(order_path: str) -> tuple[int, str, str, str]:
    """
    [FIX] 새 RUN 감지 로직 개선:
    1. manager stdout에서 TARGET_RUN_PATH 파싱 (우선)
    2. fallback: LastWriteTime 기준 가장 최신 RUN
    """
    before = list_runs()
    proc = subprocess.run(
        [sys.executable, str(MANAGER), "--order_path", order_path], 
        capture_output=True, 
        text=True
    )
    
    # 1차: stdout에서 TARGET_RUN_PATH 파싱
    target_path = parse_target_run_path(proc.stdout)
    if target_path and os.path.isdir(target_path):
        return proc.returncode, target_path, proc.stdout, proc.stderr
    
    # 2차: 새로 생긴 RUN 폴더 탐지 (LastWriteTime 기준)
    after = list_runs()
    new = list(after - before)
    
    if not new:
        return proc.returncode, "", proc.stdout, proc.stderr
    
    # [FIX] len==1 조건 제거, 가장 최신 RUN 선택
    new.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    run_path = new[0]  # 가장 최신
    
    return proc.returncode, run_path, proc.stdout, proc.stderr

def count_order_lines(order_path: str) -> int:
    """주문서 라인 수 카운트"""
    if not os.path.exists(order_path):
        return 0
    with open(order_path, "r", encoding="utf-8", errors="ignore") as f:
        return sum(1 for line in f if line.strip())

def verify_run(run_path: str, expected_missions: int) -> tuple[bool, dict]:
    """
    [FIX] 동적 expected_missions 지원 (주문서 줄 수 기준)
    """
    run = Path(run_path)
    req = ["verify_report.json", "stamp_manifest.json", "final_audit.json", "exitcode.txt"]
    state = {k: (run / k).exists() for k in req}
    
    # receipts 검증 (동적 기준)
    rec_dir = run / "receipts" / "mission"
    rec_cnt = len(list(rec_dir.glob("*.json"))) if rec_dir.exists() else 0
    state["receipts_count"] = rec_cnt
    state["receipts_expected"] = expected_missions
    state["receipts_match"] = (rec_cnt >= expected_missions)
    
    # api_receipt.jsonl 라인 수 검증
    api_receipt_path = run / "api_receipt.jsonl"
    api_lines = 0
    if api_receipt_path.exists():
        with open(api_receipt_path, "r", encoding="utf-8", errors="ignore") as f:
            api_lines = sum(1 for _ in f)
    state["api_lines"] = api_lines
    state["api_lines_match"] = (api_lines >= expected_missions)
    
    # blackbox 검증
    bb = run / "blackbox_log.jsonl"
    state["blackbox_log.jsonl"] = bb.exists() and bb.stat().st_size > 0
    
    # exitcode 검증
    ec = "MISSING"
    if (run / "exitcode.txt").exists():
        ec = (run / "exitcode.txt").read_text(encoding="utf-8", errors="ignore").strip()
    state["exitcode_value"] = ec
    state["exitcode_is_0"] = (ec == "0")
    
    # final_audit.pass 검증 (있으면)
    audit_pass = False
    if (run / "final_audit.json").exists():
        try:
            audit_data = json.loads((run / "final_audit.json").read_text(encoding="utf-8"))
            audit_pass = audit_data.get("pass", False)
        except:
            pass
    state["audit_pass"] = audit_pass
    
    # 최종 판정
    ok = (
        all(state.get(k, False) for k in req) and
        state["receipts_match"] and
        state["api_lines_match"] and
        state["blackbox_log.jsonl"] and
        state["exitcode_is_0"] and
        state["audit_pass"]
    )
    
    return ok, state

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True)
    args = ap.parse_args()

    gate_A_static_scan()

    q = Path(args.queue)
    if not q.exists():
        print("[FAIL] queue not found", str(q))
        sys.exit(1)

    lines = [x.strip() for x in q.read_text(encoding="utf-8", errors="ignore").splitlines() if x.strip()]
    if not lines:
        print("[FAIL] queue empty")
        sys.exit(1)

    for idx, order_path in enumerate(lines, 1):
        if not os.path.exists(order_path):
            print("[FAIL] order_path missing", order_path)
            sys.exit(1)

        # [FIX] 주문서 줄 수 먼저 확인
        expected_missions = count_order_lines(order_path)
        print(f"[GUARD] ({idx}/{len(lines)}) manager --order_path {order_path}")
        print(f"[GUARD] expected_missions={expected_missions}")
        
        rc, run_path, out, err = run_manager(order_path)

        if not run_path:
            fail_run = make_guard_fail_run()
            (fail_run / "stdout_manager.txt").write_text(out or "", encoding="utf-8", errors="ignore")
            (fail_run / "stderr_manager.txt").write_text(err or "", encoding="utf-8", errors="ignore")
            append_blackbox(fail_run, {"ts": int(time.time()), "event": "NO_NEW_RUN_DETECTED", "rc": rc})
            ensure_exitcode(fail_run, 1)
            print("[FAIL_FAST] no new RUN created by manager")
            sys.exit(1)

        run_dir = Path(run_path)
        (run_dir / "stdout_manager.txt").write_text(out or "", encoding="utf-8", errors="ignore")
        (run_dir / "stderr_manager.txt").write_text(err or "", encoding="utf-8", errors="ignore")

        # [FIX] 동적 expected_missions 전달
        ok, state = verify_run(run_path, expected_missions)
        append_blackbox(run_dir, {"ts": int(time.time()), "event": "GUARD_VERIFY", "rc": rc, "state": state})

        if (rc != 0) or (not ok):
            append_blackbox(run_dir, {"ts": int(time.time()), "event": "WHY_STOP", "rc": rc, "state": state})
            ensure_exitcode(run_dir, 1)
            print("[FAIL_FAST] stop on run", run_path)
            print("STATE", json.dumps(state, indent=2, ensure_ascii=False))
            sys.exit(1)

        print("[PASS] run", run_path)

    sys.exit(0)

if __name__ == "__main__":
    main()
