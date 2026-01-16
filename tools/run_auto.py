import os, subprocess, time

def run_cmd(cmd):
    print(f"\n>>> EXEC: {cmd}")
    subprocess.run(cmd, shell=True)

def auto_cycle():
    python = r"C:\Users\00\PycharmProjects\PythonProject\.venv\Scripts\python.exe"
    manager = r"C:\g7core\g7_v1\main\manager.py"
    
    print("[AUTO_RUN] Starting 24h Cycle Loop...")
    
    # 1. SMOKE3
    run_cmd(f"{python} {manager} SMOKE3.txt")
    
    # 2. A120
    run_cmd(f"{python} {manager} REAL120_A.txt")
    
    # 3. B120
    run_cmd(f"{python} {manager} REAL120_B.txt")
    
    print("[AUTO_RUN] Cycle Complete. Waiting 10 seconds before next check (Mocking Sleep)...")
    time.sleep(10)

if __name__ == "__main__":
    auto_cycle()

# [PHASE3_WELD] box01_half2_seq101 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq101
# TIMESTAMP: 2026-01-10 22:47:21.047122

# [PHASE3_WELD] box01_half2_seq102 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq102
# TIMESTAMP: 2026-01-10 22:47:22.184298

# [PHASE3_WELD] box01_half2_seq103 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq103
# TIMESTAMP: 2026-01-10 22:47:23.305957

# [PHASE3_WELD] box01_half2_seq104 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq104
# TIMESTAMP: 2026-01-10 22:47:24.434708

# [PHASE3_WELD] box01_half2_seq105 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq105
# TIMESTAMP: 2026-01-10 22:47:25.554951

# [PHASE3_WELD] box01_half2_seq106 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq106
# TIMESTAMP: 2026-01-10 22:47:26.674524

# [PHASE3_WELD] box01_half2_seq107 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq107
# TIMESTAMP: 2026-01-10 22:47:27.796702

# [PHASE3_WELD] box01_half2_seq108 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq108
# TIMESTAMP: 2026-01-10 22:47:28.918307

# [PHASE3_WELD] box01_half2_seq109 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq109
# TIMESTAMP: 2026-01-10 22:47:30.040715

# [PHASE3_WELD] box01_half2_seq110 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq110
# TIMESTAMP: 2026-01-10 22:47:31.164280

# [PHASE3_WELD] box01_half2_seq111 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq111
# TIMESTAMP: 2026-01-10 22:47:32.285267

# [PHASE3_WELD] box01_half2_seq112 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq112
# TIMESTAMP: 2026-01-10 22:47:33.407265

# [PHASE3_WELD] box01_half2_seq113 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq113
# TIMESTAMP: 2026-01-10 22:47:34.525990

# [PHASE3_WELD] box01_half2_seq114 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq114
# TIMESTAMP: 2026-01-10 22:47:35.643391

# [PHASE3_WELD] box01_half2_seq115 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq115
# TIMESTAMP: 2026-01-10 22:47:36.766392

# [PHASE3_WELD] box01_half2_seq116 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq116
# TIMESTAMP: 2026-01-10 22:47:37.887143

# [PHASE3_WELD] box01_half2_seq117 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq117
# TIMESTAMP: 2026-01-10 22:47:39.003952

# [PHASE3_WELD] box01_half2_seq118 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq118
# TIMESTAMP: 2026-01-10 22:47:40.129290

# [PHASE3_WELD] box01_half2_seq119 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq119
# TIMESTAMP: 2026-01-10 22:47:41.245434

# [PHASE3_WELD] box01_half2_seq120 | DEVLOG_AUTO_DAILY
# OBJECTIVE: Enhance tools/run_auto.py with 23:00 daily summary logic for box01_half2_seq120
# TIMESTAMP: 2026-01-10 22:47:42.370616

# [G7X_PHASE3_WELD] box01_half2_seq097 | 2026-01-10 23:27:53.569397

# [G7X_PHASE3_WELD] box01_half2_seq098 | 2026-01-10 23:27:54.690389

# [G7X_PHASE3_WELD] box01_half2_seq099 | 2026-01-10 23:27:55.807755

# [G7X_PHASE3_WELD] box01_half2_seq100 | 2026-01-10 23:27:56.924374

# [G7X_PHASE3_WELD] box01_half2_seq101 | 2026-01-10 23:27:58.044954

# [G7X_PHASE3_WELD] box01_half2_seq102 | 2026-01-10 23:27:59.164956

# [G7X_PHASE3_WELD] box01_half2_seq103 | 2026-01-10 23:28:00.285384

# [G7X_PHASE3_WELD] box01_half2_seq104 | 2026-01-10 23:28:01.406686

# [G7X_PHASE3_WELD] box01_half2_seq105 | 2026-01-10 23:28:02.527135

# [G7X_PHASE3_WELD] box01_half2_seq106 | 2026-01-10 23:28:03.647331

# [G7X_PHASE3_WELD] box01_half2_seq107 | 2026-01-10 23:28:04.768513

# [G7X_PHASE3_WELD] box01_half2_seq108 | 2026-01-10 23:28:05.896546

# [G7X_PHASE3_WELD] box01_half2_seq109 | 2026-01-10 23:28:07.014958

# [G7X_PHASE3_WELD] box01_half2_seq110 | 2026-01-10 23:28:08.132480

# [G7X_PHASE3_WELD] box01_half2_seq111 | 2026-01-10 23:28:09.247794

# [G7X_PHASE3_WELD] box01_half2_seq112 | 2026-01-10 23:28:10.370776

# [G7X_PHASE3_WELD] box01_half2_seq113 | 2026-01-10 23:28:11.482441

# [G7X_PHASE3_WELD] box01_half2_seq114 | 2026-01-10 23:28:12.605718

# [G7X_PHASE3_WELD] box01_half2_seq115 | 2026-01-10 23:28:13.721332

# [G7X_PHASE3_WELD] box01_half2_seq116 | 2026-01-10 23:28:14.845963

# [G7X_PHASE3_WELD] box01_half2_seq117 | 2026-01-10 23:28:15.960234

# [G7X_PHASE3_WELD] box01_half2_seq118 | 2026-01-10 23:28:17.083952

# [G7X_PHASE3_WELD] box01_half2_seq119 | 2026-01-10 23:28:18.197310

# [G7X_PHASE3_WELD] box01_half2_seq120 | 2026-01-10 23:28:19.316988
