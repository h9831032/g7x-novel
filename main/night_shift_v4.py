import argparse
import os
import sys
import time
import subprocess
from datetime import datetime

def read_queue(queue_path: str):
    with open(queue_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 큐 파일이 '\n'이 아니라 "\\n" 문자로 오염된 경우까지 방어
    content = content.replace("\\n", "\n")

    tokens = content.split()  # 모든 공백(\n, \r, \t, space) 분리
    orders = []
    for t in tokens:
        t = t.strip()
        if not t:
            continue
        if t.startswith("#"):
            continue
        orders.append(t)
    return orders

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def run_night_shift(
    python_exe: str,
    manager_py: str,
    requeue_py: str,
    queue_path: str,
    loops: int,
    between_orders_sleep_sec: int,
    mode: str,
    log_dir: str,
):
    ensure_dir(log_dir)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stdout_path = os.path.join(log_dir, f"night_{ts}_stdout.txt")
    stderr_path = os.path.join(log_dir, f"night_{ts}_stderr.txt")

    with open(stdout_path, "a", encoding="utf-8") as out_f, open(stderr_path, "a", encoding="utf-8") as err_f:
        def log_out(s: str):
            print(s)
            out_f.write(s + "\n")
            out_f.flush()

        def log_err(s: str):
            print(s, file=sys.stderr)
            err_f.write(s + "\n")
            err_f.flush()

        log_out(">>> [SYSTEM] NIGHT_SHIFT V4 START")
        log_out(f">>> [QUEUE] {queue_path}")
        log_out(f">>> [LOOPS] {loops}")
        log_out(f">>> [SLEEP_BETWEEN_ORDERS] {between_orders_sleep_sec}s")
        log_out(f">>> [MODE] {mode}")

        if not os.path.exists(queue_path):
            log_err(f">>> [FAIL_FAST] QUEUE_MISSING: {queue_path}")
            return 2
        if not os.path.exists(python_exe):
            log_err(f">>> [FAIL_FAST] PY_MISSING: {python_exe}")
            return 2
        if not os.path.exists(manager_py):
            log_err(f">>> [FAIL_FAST] MANAGER_MISSING: {manager_py}")
            return 2

        for i in range(loops):
            orders = read_queue(queue_path)
            log_out(f">>> [DEBUG] Found {len(orders)} orders to execute (loop {i+1}/{loops}).")

            if len(orders) == 0:
                log_err(">>> [FAIL_FAST] QUEUE_EMPTY")
                return 2

            for order_path in orders:
                log_out(f">>> [RUN] order_path={order_path}")

                if not os.path.exists(order_path):
                    log_err(f">>> [FAIL_FAST] ORDER_MISSING: {order_path}")
                    return 2

                cmd = [python_exe, manager_py, "--order_path", order_path, "--mode", mode]
                rc = subprocess.run(cmd, stdout=out_f, stderr=err_f).returncode
                log_out(f">>> [EXITCODE] {rc}")

                if rc != 0:
                    log_err(">>> [FAIL_FAST] STOP_ON_ERROR")
                    if requeue_py and os.path.exists(requeue_py):
                        subprocess.run([python_exe, requeue_py, order_path], stdout=out_f, stderr=err_f)
                        log_out(">>> [REQUEUE] logged to FAILBOX")
                    return rc

                # “잠자는 동안 굴리는” 핵심: 오더 1개 끝날 때마다 숨고르기
                time.sleep(max(0, between_orders_sleep_sec))

        log_out(">>> [SYSTEM] NIGHT_SHIFT V4 END (SUCCESS)")
        return 0

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--queue", required=True)
    p.add_argument("--loops", type=int, default=1)
    p.add_argument("--between_orders_sleep_sec", type=int, default=25)
    p.add_argument("--mode", default="REAL")

    p.add_argument("--python_exe", default=r"C:\Users\00\PycharmProjects\PythonProject\.venv\Scripts\python.exe")
    p.add_argument("--manager_py", default=r"C:\g7core\g7_v1\main\manager.py")
    p.add_argument("--requeue_py", default=r"C:\g7core\g7_v1\main\requeue_failbox.py")
    p.add_argument("--log_dir", default=r"C:\g7core\g7_v1\runs\NIGHTLOG")

    args = p.parse_args()

    rc = run_night_shift(
        python_exe=args.python_exe,
        manager_py=args.manager_py,
        requeue_py=args.requeue_py,
        queue_path=args.queue,
        loops=args.loops,
        between_orders_sleep_sec=args.between_orders_sleep_sec,
        mode=args.mode,
        log_dir=args.log_dir,
    )
    raise SystemExit(rc)

if __name__ == "__main__":
    main()
