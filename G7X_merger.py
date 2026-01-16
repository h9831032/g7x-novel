import os
import json
from datetime import datetime

def run_merge():
    print(f"   G7X_MSG: [PHASE 2] 데이터 병합 공정 - 중복 제거 및 최신본 선별 시작...")
    
    root_dir = r"C:\g7core\g7_v1"
    output_path = r"C:\g7core\g7_v1\output\G7X_MASTER_FULL.json"
    
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))

    # 중복 방지를 위한 딕셔너리 (파일명: {경로, 시간, 내용})
    file_map = {}
    target_files = ["REAL120_A.txt", "REAL120_B.txt", "REAL120_C.txt"]

    # [DEEP_SCAN_WITH_DEDUPLICATION]
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if filename in target_files:
                full_path = os.path.join(root, filename)
                mtime = os.path.getmtime(full_path)
                
                # 처음 발견하거나, 기존보다 더 최신 파일인 경우 교체
                if filename not in file_map or mtime > file_map[filename]['mtime']:
                    file_map[filename] = {
                        'path': full_path,
                        'mtime': mtime,
                        'content': ""
                    }

    master_data = []
    for filename in target_files:
        if filename in file_map:
            path = file_map[filename]['path']
            print(f"   G7X_MSG: >>> [SELECTED] {filename} (최신본 채택: {path})")
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                master_data.append({
                    "truck": filename,
                    "source_path": path,
                    "content": content,
                    "timestamp": str(datetime.fromtimestamp(file_map[filename]['mtime']))
                })

    if len(master_data) == len(target_files):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=4)
        print(f"   G7X_MSG: [SUCCESS] 360개 오더 병합 완료. 위치: {output_path}")
    else:
        print(f"   G7X_MSG: [FAIL] 필수 파일이 부족합니다. (확보: {len(master_data)}/3)")

if __name__ == "__main__":
    run_merge()