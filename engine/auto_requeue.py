import os, json, shutil

class AutoRequeue:
    def __init__(self, root=r"C:\g7core\g7_v1"):
        self.root = root
        self.fail_box = os.path.join(self.root, "runs", "FAIL_BOX")
        self.max_retry = 3

    def process(self):
        if not os.path.exists(self.fail_box): return
        
        for item in os.listdir(self.fail_box):
            path = os.path.join(self.fail_box, item)
            reason_path = os.path.join(path, "fail_reason.json")
            
            retry_count = 0
            if os.path.exists(reason_path):
                with open(reason_path, "r") as f:
                    data = json.load(f)
                    retry_count = data.get("retry_count", 0)

            if retry_count < self.max_retry:
                print(f"   [REQUEUE] Retrying {item} (Attempt {retry_count+1}/{self.max_retry})")
                # 여기서 실제 재큐 로직은 복잡하므로, 일단 로그만 남기고 다음 스텝에서 manager가 처리하도록 구성
                # (실제 구현 시 GPTORDER로 다시 밀어넣거나 함. 현재는 Logic Placeholder)
            else:
                print(f"   [STOP] {item} failed 3 times. Manual check required.")
