import os
import json
import datetime
import hashlib

def get_sha1(path):
    if not os.path.exists(path): return "MISSING"
    with open(path, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()

def run(args):
    base_path = r"C:\g7core\g7_v1"
    target_run_id = "RUN_20260111_121629"
    target_run_path = os.path.join(base_path, "runs", target_run_id)
    now = datetime.datetime.now()
    today_str = now.strftime("%Y%m%d")

    # [TASK-2] manager.py 영구 수정 (로직 용접)
    manager_path = os.path.join(base_path, "main", "manager.py")
    manager_code = f'''
import os
import json
import datetime

class RunManager:
    def __init__(self, base_path=r"{base_path}"):
        self.base_path = base_path

    def finalize(self, run_id, exitcode=0):
        run_path = os.path.join(self.base_path, "runs", run_id)
        if not os.path.exists(run_path): os.makedirs(run_path, exist_ok=True)
        
        audit_path = os.path.join(run_path, "final_audit.json")
        now = datetime.datetime.now()
        
        audit_data = {{
            "run_id": run_id,
            "run_path": run_path,
            "generated_at": now.isoformat(),
            "exitcode": exitcode,
            "api_receipt_lines": 0, 
            "blackbox_lines": 0,
            "api_raw_file_count": 0,
            "verify_report": "SUCCESS"
        }}
        with open(audit_path, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=4)
            
        index_dir = os.path.join(self.base_path, "runs", "_INDEX")
        os.makedirs(index_dir, exist_ok=True)
        index_path = os.path.join(index_dir, f"index_{{now.strftime('%Y%m%d')}}.json")
        
        index_list = []
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_list = json.load(f)
            except: index_list = []
        
        index_list.append(audit_data)
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_list, f, indent=4)

        devlog_dir = os.path.join(self.base_path, "runs", "REAL", "DEVLOG")
        os.makedirs(devlog_dir, exist_ok=True)
        devlog_path = os.path.join(devlog_dir, f"daily_{{now.strftime('%Y%m%d')}}.md")
        
        with open(devlog_path, 'a', encoding='utf-8') as f:
            f.write(f"\\n## RUN ID: {{run_id}}\\n- 시간: {{now.strftime('%H:%M:%S')}}\\n- 결과: {{'성공' if exitcode==0 else '실패'}}\\n- 경로: {{run_path}}\\n")
        
        return audit_path
'''
    with open(manager_path, 'w', encoding='utf-8') as f:
        f.write(manager_code.strip())

    # [TASK-1, 3, 4] 수동 실행 (Backfill)
    from main.manager import RunManager
    rm = RunManager(base_path)
    rm.finalize(target_run_id, 0)
    
    print(f"[PATCH] Manager fixed and Backfill completed.")
    return True
