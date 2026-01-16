# C:\g7core\g7_v1\tools\order_gen_lib.py
import os, json, hashlib

def generate_orders(unit, repeat, run_id, out_dir, task_type="TASK_V2"):
    """표준 오더 생성"""
    target = unit * repeat
    orders = []
    for i in range(1, target + 1):
        orders.append(create_order_obj(f"ORDER_{i:04d}", task_type, run_id))
    return write_order_files(orders, out_dir)

def create_order_obj(order_id, task_type, run_id, payload=None):
    """오더 객체 표준 스키마"""
    return {
        "order_id": order_id,
        "task_type": task_type,
        "run_id": run_id,
        "payload": payload or {"job": "standard_process"}
    }

def write_order_files(orders, out_dir):
    if not os.path.exists(out_dir): os.makedirs(out_dir, exist_ok=True)
    for order in orders:
        with open(os.path.join(out_dir, f"{order['order_id']}.json"), 'w', encoding='utf-8') as f:
            json.dump(order, f, indent=4)
    return len(orders)

def get_file_hash(file_path):
    if not os.path.exists(file_path): return None
    with open(file_path, "rb") as f: return hashlib.sha1(f.read()).hexdigest()