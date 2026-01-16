# C:\g7core\g7_v1\tools\create_orders_quick240.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.order_gen_lib import generate_orders

if __name__ == "__main__":
    # SSOT 라이브러리 호출 래퍼
    generate_orders(unit=120, repeat=2, run_id="MANUAL_QUICK", out_dir="C:\\g7core\\g7_v1\\runs\\MANUAL_QUICK\\queue\\work_orders", task_type="PATCH_VERIFY")
    print("SUCCESS: Wrapper execution via order_gen_lib.")