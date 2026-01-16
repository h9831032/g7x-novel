# C:\g7core\g7_v1\engine\basic_engine\blackbox_v1.py
import json, os, datetime, hashlib

class BlackBox:
    def __init__(self, run_dir):
        self.log_path = os.path.join(run_dir, "blackbox_log.jsonl")

    def record(self, order_id, request_data, response_raw):
        # [MUST_NO_SIM] raw 응답 및 해시 저장
        resp_str = str(response_raw)
        entry = {
            "ts": datetime.datetime.now().isoformat(),
            "order_id": order_id,
            "sha1": hashlib.sha1(resp_str.encode()).hexdigest(),
            "request": request_data,
            "response_snippet": resp_str[:200],
            "response_full_path": f"raw_{order_id}.txt"
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")