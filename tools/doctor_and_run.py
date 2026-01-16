import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def newest_run_dir(root: Path) -> Path | None:
    runs = root / "runs"
    if not runs.exists():
        return None
    cands = [p for p in runs.iterdir() if p.is_dir() and p.name.startswith("RUN_")]
    if not cands:
        return None
    cands.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return cands[0]

def tail_text(p: Path, n_lines: int = 120) -> str:
    if not p.exists():
        return ""
    try:
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        return "\n".join(lines[-n_lines:])
    except Exception as e:
        return f"[TAIL_READ_FAIL] {e}"

def contract_scan(manager_text: str) -> dict:
    need_tokens = [
        "api_raw",
        "exitcode",
        "verify_report",
        "final_audit",
        "stamp_manifest",
        "api_receipt",
        "blackbox",
    ]
    found = {t: (t in manager_text) for t in need_tokens}
    has_order_path = ("--order_path" in manager_text)
    has_list = ("--list" in manager_text)
    return {
        "has_order_path": has_order_path,
        "has_list": has_list,
        "tokens": found,
        "tokens_ok_count": sum(1 for v in found.values() if v),
        "tokens_total": len(found),
    }

def load_order_lines(order_path: Path) -> list[str]:
    lines = []
    for raw in order_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        lines.append(s)
    return lines

def load_work_catalog(work_catalog_path: Path):
    try:
        obj = json.loads(work_catalog_path.read_text(encoding="utf-8", errors="ignore"))
        return obj
    except Exception:
        return None

def ensure_nightlog(root: Path) -> Path:
    p = root / "runs" / "NIGHTLOG"
    p.mkdir(parents=True, exist_ok=True)
    return p

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--py", required=True)
    ap.add_argument("--order", required=True)
    args = ap.parse_args()

    root = Path(args.root)
    py = Path(args.py)
    order = Path(args.order)

    if not root.exists():
        print(f"[FATAL] ROOT_MISSING: {root}")
        return 10
    if not py.exists():
        print(f"[FATAL] PY_MISSING: {py}")
        return 11
    if not order.exists():
        print(f"[FATAL] ORDER_MISSING: {order}")
        return 12

    manager = root / "main" / "manager.py"
    if not manager.exists():
        print(f"[FATAL] MANAGER_MISSING: {manager}")
        return 13

    manager_text = manager.read_text(encoding="utf-8", errors="ignore")
    cs = contract_scan(manager_text)

    print("[CHECK] manager_contract")
    print(json.dumps(cs, ensure_ascii=False, indent=2))

    # 1) CLI 불일치 즉사 (예전에 --list만 받던 버전 흔적이 있었음)
    if not cs["has_order_path"]:
        print("[FAIL] manager.py가 --order_path를 안 받는 버전이다. (엔트리 혼입)")
        print("[HINT] manager.py 백업/정상본으로 복원 필요")
        return 20

    # 2) 엔진/카탈로그 점검 (있는지부터)
    engine = root / "engine" / "basic_engine_v29.py"
    work_catalog = root / "engine" / "work_catalog_v3.json"
    mission_jsonl = root / "mission_catalog_phase3_REAL.jsonl"
    converter = root / "tools" / "convert_catalog_jsonl_to_work_catalog.py"

    print("[CHECK] files_exist")
    print(f"  engine_basic: {engine.exists()}  {engine}")
    print(f"  work_catalog: {work_catalog.exists()}  {work_catalog}")
    print(f"  mission_jsonl: {mission_jsonl.exists()}  {mission_jsonl}")
    print(f"  converter: {converter.exists()}  {converter}")

    # 3) work_catalog 없으면 자동 생성 시도 (있을 때는 스킵)
    if (not work_catalog.exists()) and mission_jsonl.exists() and converter.exists():
        print("[DO] build_work_catalog")
        r = subprocess.run([str(py), str(converter), str(mission_jsonl), str(work_catalog)],
                           cwd=str(root), capture_output=True, text=True)
        print(f"  build_exitcode={r.returncode}")
        if r.stdout:
            print("  build_stdout_tail:")
            print("\n".join(r.stdout.splitlines()[-40:]))
        if r.stderr:
            print("  build_stderr_tail:")
            print("\n".join(r.stderr.splitlines()[-80:]))
        if r.returncode != 0 or (not work_catalog.exists()):
            print("[FAIL] work_catalog 생성 실패 → 여기서 끝")
            return 30

    # 4) 주문서 라인과 work_catalog 매칭 (대부분 미스면 “전량 필터/스킵” 난다)
    order_lines = load_order_lines(order)
    print(f"[CHECK] order_lines_count={len(order_lines)}")

    cat_obj = None
    cat_keys = None
    if work_catalog.exists():
        cat_obj = load_work_catalog(work_catalog)
        if isinstance(cat_obj, dict):
            cat_keys = set(cat_obj.keys())
        elif isinstance(cat_obj, list):
            # list of items with "id"?
            ids = []
            for it in cat_obj:
                if isinstance(it, dict) and "id" in it:
                    ids.append(str(it["id"]))
            cat_keys = set(ids) if ids else None

    if cat_keys is not None:
        missing = [x for x in order_lines if x not in cat_keys]
        print(f"[CHECK] catalog_match missing={len(missing)} / total={len(order_lines)}")
        if missing:
            print("[SAMPLE] missing_first_20")
            for x in missing[:20]:
                print("  " + x)

        # missing이 너무 많으면 실전 금지
        if len(order_lines) > 0 and (len(missing) / max(1, len(order_lines))) > 0.6:
            print("[FAIL] 주문서의 대부분이 work_catalog에 없다 → 전량 스킵/필터 가능성 매우 큼")
            return 40
    else:
        print("[WARN] work_catalog 키 구조를 못 읽음(형식이 다를 수 있음). 그래도 실행은 해봄.")

    # 5) 실행 + 로그 캡처
    nightlog = ensure_nightlog(root)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outp = nightlog / f"doctor_{ts}_stdout.txt"
    errp = nightlog / f"doctor_{ts}_stderr.txt"

    print("[RUN] manager --order_path")
    cmd = [str(py), str(manager), "--order_path", str(order)]
    print("  " + " ".join(cmd))

    p = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True)
    outp.write_text(p.stdout or "", encoding="utf-8", errors="ignore")
    errp.write_text(p.stderr or "", encoding="utf-8", errors="ignore")
    print(f"[DONE] proc_exitcode={p.returncode}")
    print(f"[LOG] {outp}")
    print(f"[LOG] {errp}")

    # 6) 최신 RUN 검문
    nr = newest_run_dir(root)
    if nr is None:
        print("[FAIL] RUN 폴더가 아예 안 생김")
        print("[TAIL stderr]")
        print(tail_text(errp, 120))
        return 50

    print(f"[CHECK] newest_run={nr}")
    api_raw_dir = nr / "api_raw"
    api_raw_cnt = len(list(api_raw_dir.glob("*"))) if api_raw_dir.exists() else 0

    need = {
        "final_audit.json": (nr / "final_audit.json").exists(),
        "verify_report.json": (nr / "verify_report.json").exists(),
        "stamp_manifest.json": (nr / "stamp_manifest.json").exists(),
        "api_receipt.jsonl": (nr / "api_receipt.jsonl").exists(),
        "blackbox_log.jsonl": (nr / "blackbox_log.jsonl").exists(),
        "exitcode.txt": (nr / "exitcode.txt").exists(),
    }
    print("[CHECK] evidence_exists")
    print(json.dumps(need, ensure_ascii=False, indent=2))
    print(f"[CHECK] api_raw_count={api_raw_cnt}")

    if not need["exitcode.txt"]:
        print("[FAIL] exitcode.txt가 없다 = manager가 finalize/FAIL_FAST까지 못 감(중간 크래시/조기종료)")
        print("[TAIL stderr]")
        print(tail_text(errp, 160))
        return 60

    exitcode = (nr / "exitcode.txt").read_text(encoding="utf-8", errors="ignore").strip()
    print(f"[CHECK] run_exitcode={exitcode}")

    # PASS 조건: api_raw >= 1 + exitcode=0 (최소 통과)
    if exitcode == "0" and api_raw_cnt >= 1:
        print("[PASS] 최소 1발 관통 성공. 이제 120/600 확장 가능.")
        return 0

    print("[FAIL] exitcode!=0 또는 api_raw==0 → 실전 금지")
    print("[TAIL stderr]")
    print(tail_text(errp, 160))
    return 70

if __name__ == "__main__":
    raise SystemExit(main())
