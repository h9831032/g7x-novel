import os
import shutil
import glob
import sys
from datetime import datetime

def run_organizer():
    # 1. 파이참 venv 및 프로젝트 루트 경로 자동 인식
    # 현재 파일(plugins/daily_organizer.py) 기준 상위 폴더를 루트로 설정
    current_file_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_file_path))
    os.chdir(project_root)

    print(f">>> [SYSTEM] Project Root: {project_root}")
    print(f">>> [SYSTEM] Using Interpreter: {sys.executable}")

    # 2. 이동 대상 파일 정의
    target_files = [
        "daily_*.md", "test_prompt.txt", "verify_report.json",
        "truck_verify_report.json", "bundle_packet.jsonl",
        "exitcode.txt", "hash_manifest.json", "stderr.txt", "stdout.txt"
    ]

    # 3. 날짜별 폴더 생성 (daily/YYYY/MM-DD)
    now = datetime.now()
    target_dir = os.path.join(project_root, "daily", now.strftime("%Y"), now.strftime("%m-%d"))
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        print(f">>> [CREATE] Directory created: {target_dir}")

    # 4. 파일 이동 집행
    moved_count = 0
    for pattern in target_files:
        files = glob.glob(os.path.join(project_root, pattern))
        for f in files:
            file_name = os.path.basename(f)
            dest = os.path.join(target_dir, file_name)
            try:
                if os.path.exists(dest):
                    os.remove(dest)
                shutil.move(f, dest)
                print(f">>> [MOVED] {file_name}")
                moved_count += 1
            except Exception as e:
                print(f">>> [ERROR] {file_name} move failed: {e}")

    print("-" * 40)
    print(f">>> [COMPLETED] Total {moved_count} files organized into {target_dir}")
    print("-" * 40)

if __name__ == "__main__":
    run_organizer()