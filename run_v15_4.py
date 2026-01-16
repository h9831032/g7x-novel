import os
import sys
import csv
import hashlib
from pathlib import Path

# [MANDATE] Constants derived from physical requirements
MIN_RECOGNITION_LIMIT = 60   # 권당 최소 인정 청크 (60 미만은 파기)
COMPLETE_THRESHOLD = 100    # 완공 인정 기준 (100 이상만 Complete)

def get_receipt_stats(file_list):
    """실제 파일 시스템에서 통계 수치를 물리적으로 계산 (NO_DUMMY)"""
    total_words = 0
    total_chars = 0
    for f in file_list:
        content = f.read_text(encoding='utf-8', errors='ignore')
        total_words += len(content.split())
        total_chars += len(content)
    return total_words, total_chars

def generate_sha256(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def run_engine():
    input_path = Path(r'C:\g7core\g7_v1\input_chunks')
    output_path = Path(r'C:\g7core\g7_v1\output_reports')
    
    # 1. FAIL_FAST: 파일 부재 체크
    shards = list(input_path.glob("*.txt"))
    if not shards:
        print(f"ERROR: NO_DATA_FOUND at {input_path}. Place your .txt shards there.")
        sys.exit(1)

    # 2. WID 기반 그룹화
    novel_map = {}
    for s in shards:
        # 파일명 규격: WID_001-XXXX.txt
        wid = s.name.split('-')[0]
        if wid not in novel_map: novel_map[wid] = []
        novel_map[wid].append(s)

    complete_stack = []
    incomplete_stack = []

    # 3. 실증 데이터 계산 및 분류
    for wid, files in novel_map.items():
        count = len(files)
        
        # 60청크 미달 시 즉시 중단 또는 기록 제외 (FAIL_FAST)
        if count < MIN_RECOGNITION_LIMIT:
            print(f"CRITICAL: {wid} failed to meet MIN_RECOGNITION_LIMIT ({count} < {MIN_RECOGNITION_LIMIT})")
            continue

        words, chars = get_receipt_stats(files)
        
        receipt = {
            "WID": wid,
            "chunks_used": count,
            "physical_word_count": words,
            "physical_char_count": chars,
            "avg_chunk_density": round(words / count, 2),
            "integrity_hash": generate_sha256(files[0])
        }

        if count >= COMPLETE_THRESHOLD:
            complete_stack.append(receipt)
        else:
            incomplete_stack.append(receipt)

    # 4. 결과 출력 (영수증 발행)
    def export(data, name):
        if not data: return
        p = output_path / name
        with open(p, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f">>> [G7X] Exported: {name} | Count: {len(data)}")

    export(complete_stack, "quality_matrix_complete.csv")
    export(incomplete_stack, "quality_matrix_incomplete.csv")

    if not complete_stack and not incomplete_stack:
        print("ERROR: All data filtered out. Check chunk counts.")
        sys.exit(1)

if __name__ == '__main__':
    run_engine()
