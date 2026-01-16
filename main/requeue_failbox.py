import sys
import os
from datetime import datetime

def requeue(failed_order):
    """실패 오더를 정제하여 FAILBOX에 기록 (오염 경로 세척)"""
    # 모든 공백 및 개행 문자 물리적 제거
    clean_order = "".join(failed_order.split())
    failbox_path = r"C:\g7core\g7_v1\GPTORDER\FAILBOX_QUEUE.txt"
    os.makedirs(os.path.dirname(failbox_path), exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(failbox_path, "a", encoding='utf-8') as f:
        f.write(f"[{timestamp}] FAILED: {clean_order}\n")
    
    print(f">>> [REQUEUE_SUCCESS] Added to FailBox: {clean_order}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        requeue(sys.argv[1])