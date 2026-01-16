import time

def run_real_logic(orders):
    """
    6x20 박스 그리드 + 3+3 체크포인트(연속 3회 실패 시 셧다운)
    """
    total_orders = orders
    batch_size = 20
    boxes = [total_orders[i:i + batch_size] for i in range(0, len(total_orders), batch_size)]
    
    consecutive_fails = 0
    completed_count = 0

    print(f"[SYSTEM] REAL MODE START: Total {len(boxes)} boxes (120 orders)")

    for idx, box in enumerate(boxes):
        print(f"\n[BOX {idx+1}/6] Processing...")
        
        for order in box:
            # [3+3 Checkpoint]
            if consecutive_fails >= 3:
                print("[CRITICAL] 3 Consecutive Fails detected. EMERGENCY STOP.")
                return "FAIL_STOP"

            try:
                # 여기서 실제 Gemini API 호출 (예시 구조)
                # result = call_gemini_api(order) 
                time.sleep(0.1) # 생산 속도 조절
                
                success = True # API 결과 가정
                if success:
                    completed_count += 1
                    consecutive_fails = 0 
                else:
                    raise Exception("API_ERROR")
            except:
                consecutive_fails += 1
                print(f"[WARN] Order Failed. Consecutive Fails: {consecutive_fails}")

        print(f"[BOX {idx+1}/6] COMPLETED. (Total: {completed_count}/120)")
    
    return "ALL_PASS"

if __name__ == "__main__":
    # 개별 테스트용
    sample_orders = [f"order_{i}" for i in range(120)]
    run_real_logic(sample_orders)