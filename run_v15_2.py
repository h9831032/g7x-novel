import os
import sys
import csv
import hashlib
from pathlib import Path

# MANDATES
MIN_CHUNKS_THRESHOLD = 100  # [NEXT] 지시사항: 100개 기준

def get_sha256(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def process_v15_2():
    input_dir = Path(r'C:\g7core\g7_v1\input_chunks')
    output_dir = Path(r'C:\g7core\g7_v1\output_reports')
    
    # 1. DYNAMIC_LOAD & PATH_VERIFICATION
    if not input_dir.exists():
        print(f"ERROR: Input directory {input_dir} not found.")
        sys.exit(1)
        
    chunk_files = list(input_dir.glob("*.txt"))
    total_found = len(chunk_files)
    
    if total_found == 0:
        print("ERROR: NO_DATA_FOUND. System Exit to prevent dummy logic.")
        sys.exit(1)
    
    print(f">>> [G7X] Shards Detected: {total_found}")

    # 2. Grouping by Novel ID (WID)
    novel_groups = {}
    for f in chunk_files:
        wid = f.name.split('-')[0] # 규격: WID_001-hash.txt 가정
        if wid not in novel_groups:
            novel_groups[wid] = []
        novel_groups[wid].append(f)

    complete_results = []
    incomplete_results = []

    # 3. Processing with Evidence Receipt
    for wid, files in novel_groups.items():
        chunks_count = len(files)
        total_word_count = 0
        
        # 실제 파일 시스템 수치 동적 로드 (NO_DUMMY)
        for f in files:
            with open(f, 'r', encoding='utf-8', errors='ignore') as content:
                total_word_count += len(content.read().split())
        
        # Score Calculation (Receipt Based)
        # 단순 상수가 아닌 단어수와 청크수의 상관관계로 점수 산출 예시
        quality_score = round(min(100, (total_word_count / (chunks_count * 200)) * 100), 2)
        
        receipt = {
            "wid": wid,
            "chunks_used": chunks_count,
            "total_words": total_word_count,
            "avg_words_per_chunk": round(total_word_count / chunks_count, 1) if chunks_count > 0 else 0,
            "quality_score": quality_score,
            "sha256_sample": get_sha256(files[0]) if files else "N/A"
        }

        if chunks_count >= MIN_CHUNKS_THRESHOLD:
            complete_results.append(receipt)
        else:
            incomplete_results.append(receipt)

    # 4. DETERMINISTIC_OUTPUT
    def save_csv(data, filename):
        if not data:
            return
        path = output_dir / filename
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.DictWriter(f, fieldnames=data[0].keys())
            w.writeheader()
            w.writerows(data)
        print(f">>> [G7X] Exported: {filename} ({len(data)} records)")

    save_csv(complete_results, "quality_matrix_complete.csv")
    save_csv(incomplete_results, "quality_matrix_incomplete.csv")

    if not complete_results and not incomplete_results:
        print("CRITICAL: Empty processing result. Check input file patterns.")
        sys.exit(1)

if __name__ == "__main__":
    process_v15_2()
