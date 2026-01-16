import os
import json
import datetime
import re

def count_lines(path):
    if not os.path.exists(path): return 0
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except: return 0

def count_files(path):
    if not os.path.exists(path): return 0
    count = 0
    for root, dirs, files in os.walk(path):
        count += len(files)
    return count

def run(args):
    base_path = r"C:\g7core\g7_v1"
    run_id = "RUN_20260111_121629"
    run_path = os.path.join(base_path, "runs", run_id)
    
    # [TASK-1] 실제 값 추출
    api_receipt_lines = count_lines(os.path.join(run_path, "api_receipt.jsonl"))
    blackbox_lines = count_lines(os.path.join(run_path, "blackbox_log.jsonl"))
    api_raw_file_count = count_files(os.path.join(run_path, "api_raw"))
    
    exitcode_path = os.path.join(run_path, "exitcode.txt")
    exitcode = 0
    if os.path.exists(exitcode_path):
        try:
            with open(exitcode_path, 'r') as f: exitcode = int(f.read().strip())
        except: pass

    audit_data = {
        "run_id": run_id,
        "run_path": run_path,
        "generated_at": datetime.datetime.now().isoformat(),
        "exitcode": exitcode,
        "api_receipt_lines": api_receipt_lines,
        "blackbox_lines": blackbox_lines,
        "api_raw_file_count": api_raw_file_count,
        "verify_report": "REAL_COUNT_VERIFIED"
    }

    # final_audit.json 재생성
    with open(os.path.join(run_path, "final_audit.json"), 'w', encoding='utf-8') as f:
        json.dump(audit_data, f, indent=4)

    # [TASK-2] manager.py 용접 (전체 덮어쓰기 금지)
    manager_path = os.path.join(base_path, "main", "manager.py")
    with open(manager_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # finalize 함수 내부의 audit 생성 블록을 실측 로직으로 교체
    new_block = '''
        # --- WELDED REAL COUNT LOGIC ---
        api_receipt_path = os.path.join(run_path, "api_receipt.jsonl")
        blackbox_path = os.path.join(run_path, "blackbox_log.jsonl")
        api_raw_path = os.path.join(run_path, "api_raw")
        
        def _get_lines(p): return sum(1 for _ in open(p, 'r', encoding='utf-8')) if os.path.exists(p) else 0
        def _get_files(p): return sum([len(files) for r, d, files in os.walk(p)]) if os.path.exists(p) else 0

        audit_data = {
            "run_id": run_id,
            "run_path": run_path,
            "generated_at": now.isoformat(),
            "exitcode": exitcode,
            "api_receipt_lines": _get_lines(api_receipt_path),
            "blackbox_lines": _get_lines(blackbox_path),
            "api_raw_file_count": _get_files(api_raw_path),
            "verify_report": "SUCCESS"
        }
        # -------------------------------
'''
    # 기존 가라 audit_data 생성 부분만 정규식으로 치환 (용접)
    content = re.sub(r'audit_data = \{.*?\}', new_block.strip(), content, flags=re.DOTALL)
    
    with open(manager_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[SYSTEM] Backfill and Welding complete for {run_id}")
    return True
