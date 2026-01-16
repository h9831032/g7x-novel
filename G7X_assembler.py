import json
import os

def run_assembler():
    print(f"   G7X_MSG: [PHASE 4] 최종 데이터 조립 및 바인딩 시작...")
    parsed_path = r"C:\g7core\g7_v1\output\G7X_PARSED_360.json"
    final_output = r"C:\g7core\g7_v1\output\G7X_FINAL_PRODUCTION.txt"
    
    if not os.path.exists(parsed_path):
        print("   G7X_MSG: [ERROR] 파싱된 데이터를 찾을 수 없습니다.")
        return

    with open(parsed_path, 'r', encoding='utf-8') as f:
        all_orders = json.load(f)

    # [ASSEMBLY_LOGIC] 360개 본문을 줄바꿈과 함께 하나로 결합
    with open(final_output, 'w', encoding='utf-8') as f:
        for idx, order in enumerate(all_orders, 1):
            f.write(f"--- [ORDER #{idx:03d} | {order['header']}] ---\n")
            f.write(order['body'] + "\n\n")

    print(f"   G7X_MSG: [SUCCESS] 최종 조립 완료!")
    print(f"   G7X_MSG: >>> 완성본 파일: {final_output}")

if __name__ == "__main__":
    run_assembler()