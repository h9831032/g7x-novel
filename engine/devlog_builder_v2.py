import os
import json
from datetime import datetime

def generate_devlog():
    root = r"C:\g7core\g7_v1"
    runs_dir = os.path.join(root, "runs")
    
    # [FIX] 이름순이 아닌 '물리적 생성 시간' 순으로 정렬하여 진짜 최신 폴더 타격
    all_runs = [os.path.join(runs_dir, d) for d in os.listdir(runs_dir) if d.startswith("RUN_")]
    if not all_runs:
        print(">>> [ERROR] No RUN folders found.")
        return
    
    # 생성 시간이 가장 늦은(최신) 폴더 선택
    latest_run = max(all_runs, key=os.path.getctime)
    run_name = os.path.basename(latest_run)
    
    verify_path = os.path.join(latest_run, "verify_report.json")
    receipt_path = os.path.join(latest_run, "api_receipt.jsonl")
    
    print("-" * 60)
    print(f" G7X PHASE 3 FINAL AUDIT REPORT (TARGET: {run_name})")
    print("-" * 60)
    
    # 1. 요약 통계
    if os.path.exists(verify_path):
        with open(verify_path, 'r', encoding='utf-8') as f:
            v = json.load(f)
            print(f" [SUMMARY] TOTAL: {v.get('total', 0)} | SUCCESS: {v.get('success', 0)} | SKIP: {v.get('skip', 0)} | FAIL: {v.get('fail', 0)}")
    
    # 2. 파일 존재 여부 검전
    print("\n [FILE AUDIT]")
    files = ["api_receipt.jsonl", "blackbox_log.jsonl", "stamp_manifest.json", "exitcode.txt"]
    for f_name in files:
        status = "✅ EXISTS" if os.path.exists(os.path.join(latest_run, f_name)) else "❌ MISSING"
        print(f" - {f_name.ljust(20)}: {status}")
    
    # 3. 실전 데이터 샘플 (마지막 5건)
    print("\n [LAST 5 MISSIONS EVIDENCE]")
    if os.path.exists(receipt_path):
        with open(receipt_path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            for line in lines[-5:]:
                data = json.loads(line)
                print(f" - {data['mission_id']}: {data['model']} | Tokens: {data['tokens']} | Hash: {data['raw_sha1'][:10]}...")
    else:
        print(" (No new API calls recorded in this run - all skipped or error)")

    print("-" * 60)
    print(f" REPORT GENERATED AT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

if __name__ == "__main__":
    generate_devlog()