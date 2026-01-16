import os
import subprocess
import sys

# [1] NIGHT_QUEUE.txt 강제 초기화 (찌꺼기 제거)
queue_path = r"C:\g7core\g7_v1\GPTORDER\NIGHT_QUEUE.txt"
clean_content = (
    r"C:\g7core\g7_v1\GPTORDER\REAL_MISSION_120_A.txt" + "\n" +
    r"C:\g7core\g7_v1\GPTORDER\REAL_MISSION_120_B.txt"
)
os.makedirs(os.path.dirname(queue_path), exist_ok=True)
with open(queue_path, "w", encoding='utf-8') as f:
    f.write(clean_content)
print(f">>> [FIX] NIGHT_QUEUE.txt has been reset cleanly.")

# [2] night_shift.py 강제 덮어쓰기 (무조건 분할 로직)
night_shift_code = r'''import subprocess
import os
import sys
import argparse
import time

def run_night_shift(queue_path, loops):
    if not os.path.exists(queue_path):
        print(f">>> [ERROR] Queue file missing: {queue_path}")
        return
    
    python_exe = r"C:\Users\00\PycharmProjects\PythonProject\.venv\Scripts\python.exe"
    manager_py = r"C:\g7core\g7_v1\main\manager.py"
    requeue_py = r"C:\g7core\g7_v1\main\requeue_failbox.py"

    print(">>> [SYSTEM] NIGHT_SHIFT V3.0 (FINAL_FIX) STARTED")

    for i in range(loops):
        # [KEY FIX] read().split() handles all whitespace including \n, \r, \t, spaces
        with open(queue_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Handle potential literal backslash-n if present
            content = content.replace('\\n', '\n')
            orders = content.split()

        valid_orders = [o.strip() for o in orders if o.strip() and not o.startswith("#")]
        
        print(f">>> [DEBUG] Found {len(valid_orders)} orders to execute.")

        for order in valid_orders:
            print(f"\n>>> [NIGHT_SHIFT] Loop {i+1} | Target: {order}")
            
            cmd = [python_exe, manager_py, "--order_path", order, "--mode", "REAL"]
            
            # Flush stdout to see logs immediately
            sys.stdout.flush()
            
            result = subprocess.run(cmd)
            
            if result.returncode != 0:
                print(f">>> [FAIL_FAST] Manager Error (Code {result.returncode})")
                if os.path.exists(requeue_py):
                    subprocess.run([python_exe, requeue_py, order])
                sys.exit(1)
            
            # Brief pause between trucks
            time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", required=True)
    parser.add_argument("--loops", type=int, default=1)
    args = parser.parse_args()
    run_night_shift(args.queue, args.loops)
'''

night_shift_path = r"C:\g7core\g7_v1\main\night_shift.py"
with open(night_shift_path, "w", encoding='utf-8') as f:
    f.write(night_shift_code)
print(f">>> [FIX] night_shift.py has been updated to V3.0.")

# [3] requeue_failbox.py 생성 확인
requeue_code = r'''import sys
import os
from datetime import datetime

def requeue(failed_order):
    clean_order = "".join(failed_order.split())
    failbox_path = r"C:\g7core\g7_v1\GPTORDER\FAILBOX_QUEUE.txt"
    os.makedirs(os.path.dirname(failbox_path), exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(failbox_path, "a", encoding='utf-8') as f:
        f.write(f"[{timestamp}] FAILED: {clean_order}\n")
    print(f">>> [REQUEUE] Logged to FailBox: {clean_order}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        requeue(sys.argv[1])
'''
requeue_path = r"C:\g7core\g7_v1\main\requeue_failbox.py"
if not os.path.exists(requeue_path):
    with open(requeue_path, "w", encoding='utf-8') as f:
        f.write(requeue_code)
    print(f">>> [FIX] requeue_failbox.py created.")

# [4] 즉시 실행
print(">>> [ACTION] Launching NIGHT_SHIFT now...")
python_exe = r"C:\Users\00\PycharmProjects\PythonProject\.venv\Scripts\python.exe"
subprocess.run([python_exe, night_shift_path, "--queue", queue_path, "--loops", "1"])