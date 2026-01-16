# C:\g7core\g7_v1\main.py
import os, sys, json, time, argparse, shutil
from datetime import datetime
from plugins.night_shift_manager import NightShiftManager
from tools.order_gen_lib import generate_orders, create_order_obj, write_order_files

class G7XEngineV5:
    def __init__(self, args):
        self.args = args
        self.run_id = args.run_id
        self.base_path = "C:\\g7core\\g7_v1"
        
        # 1. 경로 봉인 (GPTORDER 용접)
        self.run_log_dir = os.path.join(self.base_path, "runs", self.run_id)
        self.order_dir = os.path.join(self.run_log_dir, "queue", "work_orders")
        self.stamp_dir = os.path.join(self.run_log_dir, "stamps")
        self.requeue_dir = os.path.join(self.run_log_dir, "queue", "requeue")
        self.inbox_dir = os.path.join(self.base_path, "GPTORDER") # 용접 지점
        self.done_dir = os.path.join(self.base_path, "ORDER", "done")
        
        for d in [self.order_dir, self.stamp_dir, self.run_log_dir, self.requeue_dir, self.inbox_dir, self.done_dir]:
            os.makedirs(d, exist_ok=True)

        self.manager = NightShiftManager(self.stamp_dir, self.requeue_dir, self.run_log_dir, self.args)

    def process_gptorder(self):
        """GPTORDER 폴더의 txt를 읽어 SSOT 오더로 변환"""
        txt_files = [f for f in os.listdir(self.inbox_dir) if f.endswith('.txt')]
        if not txt_files: return 0
        
        inbox_orders = []
        for fn in txt_files:
            file_path = os.path.join(self.inbox_dir, fn)
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                for i, line in enumerate(lines):
                    task_type = "TASK_V2"
                    payload = {"raw": line}
                    if "|" in line:
                        parts = line.split("|")
                        task_type = parts[0]
                        payload = {"content": parts[1]}
                    
                    inbox_orders.append(create_order_obj(f"GPT_{i+1:04d}", task_type, self.run_id, payload))
            
            # 처리 완료 후 이동 (재처리 방지)
            shutil.move(file_path, os.path.join(self.done_dir, fn))
        
        return write_order_files(inbox_orders, self.order_dir)

    def run(self):
        # 2. 오더 생성 및 타겟 확정 (중복 생성 방지: unit=0이면 텍스트만)
        created_count = 0
        if self.args.unit > 0:
            created_count = generate_orders(self.args.unit, self.args.repeat, self.run_id, self.order_dir)
        
        text_count = self.process_gptorder()
        self.target = created_count + text_count # TARGET은 실제 생성된 오더 총합

        print(f"TARGET_SYNC: {self.target} (Auto: {created_count}, Text: {text_count})")

        with open(os.path.join(self.run_log_dir, "order_manifest.json"), 'w') as f:
            json.dump({"run_id": self.run_id, "target": self.target, "created": self.target}, f, indent=4)

        # 3. 메인 루프 (스탬프 완주 기준)
        box_idx = 1
        while self.manager.get_stamp_count() < self.target:
            print(f"\n[BOX_START] idx={box_idx} Target={self.target} StampNow={self.manager.get_stamp_count()}")
            for half in [1, 2]:
                batch = sorted([f for f in os.listdir(self.order_dir) if f.endswith('.json')])[:3]
                if not batch: break
                for order_file in batch:
                    print(f"  > Processing: {order_file}...", end=" ", flush=True)
                    if self.manager.process_order(os.path.join(self.order_dir, order_file), box_idx, half):
                        print("DONE")
                    else:
                        print("REQUEUED")
                
                # 리큐 재투입 펌프 (자동)
                self.pump_requeue()
                
                # Half Sleep (20s)
                if self.manager.get_stamp_count() < self.target:
                    print(f"GUARD: HALF_SLEEP ({self.args.half_sleep}s)...")
                    time.sleep(self.args.half_sleep)
            
            box_idx += 1

        self.final_audit()

    def pump_requeue(self):
        requeue_files = [f for f in os.listdir(self.requeue_dir) if f.endswith('.json')]
        for f in requeue_files[:3]:
            shutil.move(os.path.join(self.requeue_dir, f), os.path.join(self.order_dir, f))

    def final_audit(self):
        stamp_count = self.manager.get_stamp_count()
        audit = {"FOUND": self.target, "STAMP_COUNT": stamp_count, "STATUS": "PASS" if stamp_count == self.target else "FAIL"}
        with open(os.path.join(self.run_log_dir, "final_audit.json"), 'w') as f: json.dump(audit, f, indent=4)
        print(f"\n==============================\nOVERALL_STATUS={audit['STATUS']}\n==============================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_id", default="auto")
    parser.add_argument("--unit", type=int, default=120)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--writer_mode", default="STUB")
    parser.add_argument("--purge", type=int, default=1)
    parser.add_argument("--real_smoke", type=int, default=0)
    parser.add_argument("--half_sleep", type=int, default=20)
    parser.add_argument("--box_sleep", type=int, default=45)
    G7XEngineV5(parser.parse_args()).run()