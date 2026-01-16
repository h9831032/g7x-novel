import json
import os

def run_filter():
    print(f"   G7X_MSG: [PHASE 3] 데이터 필터링 및 무결성 스캔 시작...")
    master_path = r"C:\g7core\g7_v1\output\G7X_MASTER_FULL.json"
    clean_path = r"C:\g7core\g7_v1\output\G7X_CLEAN_DATA.json"
    
    if not os.path.exists(master_path):
        print("   G7X_MSG: [ERROR] 마스터 파일을 찾을 수 없습니다.")
        return

    with open(master_path, 'r', encoding='utf-8') as f:
        master_data = json.load(f)

    clean_data = []
    error_count = 0

    print(f"   G7X_MSG: >>> 360개 오더 정밀 검사 중...")
    
    # [FILTERING_LOGIC]
    for entry in master_data:
        content = entry.get("content", "")
        # 1. 빈 데이터 검사 2. 최소 길이 검사 3. 에러 키워드 스캔
        if len(content.strip()) < 10 or "error" in content.lower():
            error_count += 1
            continue
        
        clean_data.append(entry)

    with open(clean_path, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=4)

    print(f"   G7X_MSG: [SUCCESS] 필터링 완료. (정상: {len(clean_data)} / 불량: {error_count})")
    print(f"   G7X_MSG: >>> 정제 데이터 저장: {clean_path}")

if __name__ == "__main__":
    run_filter()