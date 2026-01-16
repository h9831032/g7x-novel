import json
import re
import os

def run_parser():
    print(f"   G7X_MSG: [REPAIR v3] TASK_V2 규격 정밀 파싱 시작...")
    master_path = r"C:\g7core\g7_v1\output\G7X_MASTER_FULL.json"
    parsed_path = r"C:\g7core\g7_v1\output\G7X_PARSED_360.json"
    
    with open(master_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    all_orders = []
    # [TASK_V2_SPECIFIC_LOGIC] TASK_V2 패턴을 기준으로 데이터를 분할합니다.
    # 패턴 예시: TASK_V2|truck=A|box=01|payload=CHUNK_001
    pattern = re.compile(r'(TASK_V2\|truck=[A-C]\|box=\d+\|payload=CHUNK_\d+)')

    for truck in raw_data:
        content = truck['content']
        parts = pattern.split(content)
        
        # 첫 번째 요소는 헤더 이전의 쓰레기 데이터일 수 있으므로 건너뜀
        for i in range(1, len(parts), 2):
            header = parts[i].strip()
            body = parts[i+1].strip() if i+1 < len(parts) else ""
            
            # 메타데이터 추출 (트럭, 박스 번호 등)
            all_orders.append({
                "header": header,
                "body": body,
                "length": len(body)
            })

    with open(parsed_path, 'w', encoding='utf-8') as f:
        json.dump(all_orders, f, ensure_ascii=False, indent=4)

    print(f"   G7X_MSG: [SUCCESS] 파싱 완료. 총 {len(all_orders)}개 오더(TASK_V2) 복구 성공.")

if __name__ == "__main__":
    run_parser()