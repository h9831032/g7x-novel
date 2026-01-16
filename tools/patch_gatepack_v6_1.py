from __future__ import annotations
import shutil, time
from pathlib import Path

ROOT = Path(r"C:\g7core\g7_v1")
TS = time.strftime("%Y%m%d_%H%M%S")

def backup(p: Path) -> None:
    if p.exists():
        b = p.with_name(p.name + f".bak_{TS}")
        shutil.copy2(p, b)
        print("BACKUP", str(p), "->", str(b))

def write_text(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print("WRITE", str(p), "bytes", p.stat().st_size)

def main():
    p_guard = ROOT / "main" / "night_shift_guard_v5.py"
    backup(p_guard)

    guard_code = r'''
from __future__ import annotations
import argparse, glob, os, subprocess, sys, time, json
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
    "모사",
    "가라",
    "120 유닛",
    "120 units",
]

def gate_A_static_scan() -> None:
    # 핵심: guard 자기 파일은 스캔 대상에서 제외한다(자기 안의 BAN_TOKENS 때문에 오탐 발생).
    targets = [
        ROOT / "main" / "manager.py",
        ROOT / "tools" / "one_shot_night_work_600.py",
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

def pick_new_run(before: set[str]) -> str:
    after = list_runs()
    new = list(after - before)
    if len(new) == 1:
        return new[0]
    cand = list(after) if not new else new
    cand.sort(key=lambda x: os.path.getmtime(x))
    return cand[-1] if cand else ""

def ensure_exitcode(run_dir: Path, code: int) -> None:
    (run_dir / "exitcode.txt").write_text(str(code), encoding="utf-8")

def append_blackbox(run_dir: Path, obj: dict) -> None:
    bb = run_dir / "blackbox_log.jsonl"
    with bb.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def verify_run(run_path: str) -> tuple[bool, dict]:
    run = Path(run_path)
    req_files = ["verify_report.json", "stamp_manifest.json", "final_audit.json", "exitcode.txt"]
    state = {k: (run / k).exists() for k in req_files}

    rec_dir = run / "receipts" / "mission"
    rec_cnt = len(list(rec_dir.glob("*.json"))) if rec_dir.exists() else 0
    state["receipts_120"] = (rec_cnt >= 120)

    # blackbox 백필
    from blackbox_backfill_v1 import ensure_blackbox
    ensure_blackbox(str(run))
    bb = run / "blackbox_log.jsonl"
    state["blackbox_log.jsonl"] = bb.exists() and bb.stat().st_size > 0

    ec = (run / "exitcode.txt").read_text(encoding="utf-8", errors="ignore").strip() if (run / "exitcode.txt").exists() else "MISSING"
    state["exitcode_is_0"] = (ec == "0")

    ok = all(state.values())
    return ok, state

def run_manager(order_path: str) -> tuple[int, str, str, str]:
    before = list_runs()
    proc = subprocess.run([sys.executable, str(MANAGER), "--order_path", order_path], capture_output=True, text=True)
    run_path = pick_new_run(before)
    return proc.returncode, run_path, proc.stdout, proc.stderr

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

        print(f"[GUARD] ({idx}/{len(lines)}) manager --order_path {order_path}")
        rc, run_path, out, err = run_manager(order_path)
        if not run_path:
            print("[FAIL] cannot detect RUN dir")
            sys.exit(1)

        run_dir = Path(run_path)
        (run_dir / "stdout_manager.txt").write_text(out, encoding="utf-8", errors="ignore")
        (run_dir / "stderr_manager.txt").write_text(err, encoding="utf-8", errors="ignore")

        ok, state = verify_run(run_path)
        append_blackbox(run_dir, {"ts": int(time.time()), "event": "GUARD_VERIFY", "state": state})

        if (rc != 0) or (not ok):
            append_blackbox(run_dir, {"ts": int(time.time()), "event": "WHY_STOP", "rc": rc, "state": state})
            ensure_exitcode(run_dir, 1)
            print("[FAIL_FAST] stop on run", run_path)
            print("STATE", state)
            sys.exit(1)

        print("[PASS] run", run_path)

    sys.exit(0)

if __name__ == "__main__":
    main()
'''.lstrip()

    write_text(p_guard, guard_code)

if __name__ == "__main__":
    main()
