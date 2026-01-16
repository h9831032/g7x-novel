import os, sys, json, glob, subprocess

def night_shift_guard(run_path):
    """B3. FAIL_FAST 가드 로직"""
    # 1. Receipts 개수 확인
    receipts = glob.glob(os.path.join(run_path, "receipts", "mission", "*.json"))
    receipt_count = len(receipts)
    
    # B2. blackbox_log.jsonl / exitcode.txt 강제 생성
    blackbox_path = os.path.join(run_path, "blackbox_log.jsonl")
    exitcode_path = os.path.join(run_path, "exitcode.txt")
    
    evidence = {
        "verify_report.json": os.path.exists(os.path.join(run_path, "verify_report.json")),
        "stamp_manifest.json": os.path.exists(os.path.join(run_path, "stamp_manifest.json")),
        "final_audit.json": os.path.exists(os.path.join(run_path, "final_audit.json")),
        "exitcode.txt": os.path.exists(exitcode_path),
        "blackbox_log.jsonl": os.path.exists(blackbox_path),
        "receipts_120": receipt_count >= 120
    }
    
    if not all(evidence.values()):
        why_stop = f"Missing Evidence: {[k for k, v in evidence.items() if not v]}"
        with open(blackbox_path, 'a') as f: f.write(json.dumps({"WHY_STOP": why_stop}) + "\n")
        with open(exitcode_path, 'w') as f: f.write("1")
        print(f">>> [STOP] Guard Triggered: {why_stop}")
        sys.exit(1) # B3. 즉시 STOP

def run_night_shift():
    # ... 기존 큐 루프 로직 ...
    # subprocess.run(["manager.py", ...]) 실행 후
    # latest_run = get_latest_run_path()
    # night_shift_guard(latest_run)
    pass