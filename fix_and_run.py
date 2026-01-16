import os
import shutil
import glob
from datetime import datetime

def final_fix():
    print("="*50)
    print(">>> [SYSTEM] G7X EMERGENCY REPAIR START")
    print("="*50)

    # 1. 작업 경로 설정 (현재 파일 위치 기준)
    base_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_path)
    print(f">>> [INFO] Working Directory: {base_path}")

    # 2. 날짜 폴더 생성 (daily/2026/01-11 형식)
    now = datetime.now()
    year_folder = now.strftime("%Y")
    date_folder = now.strftime("%m-%d")
    
    target_dir = os.path.join(base_path, "daily", year_folder, date_folder)
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f">>> [OK] Created: {target_dir}")
    else:
        print(f">>> [OK] Folder already exists: {target_dir}")

    # 3. 정리 대상 파일 목록
    targets = [
        "daily_*.md", "test_prompt.txt", "verify_report.json",
        "truck_verify_report.json", "bundle_packet.jsonl",
        "exitcode.txt", "hash_manifest.json", "stderr.txt", "stdout.txt"
    ]

    # 4. 파일 이동 집행
    move_count = 0
    for pattern in targets:
        # 루트 경로에서 파일 찾기
        found_files = glob.glob(os.path.join(base_path, pattern))
        for src_file in found_files:
            fname = os.path.basename(src_file)
            dest_file = os.path.join(target_dir, fname)
            
            try:
                # 동일 파일 존재 시 강제 덮어쓰기
                if os.path.exists(dest_file):
                    os.remove(dest_file)
                shutil.move(src_file, dest_file)
                print(f">>> [MOVED] {fname} -> {target_dir}")
                move_count += 1
            except Exception as e:
                print(f">>> [ERROR] Failed to move {fname}: {e}")

    print("="*50)
    print(f">>> [FINAL RESULT] {move_count} FILES ORGANIZED.")
    print(">>> [STATUS] ALL SYSTEMS NORMAL. WAITING FOR NEXT ORDER.")
    print("="*50)

if __name__ == "__main__":
    final_fix()