# C:\g7core\g7_v1\engine\basic_engine\stamp_v1.py
import json, os

class StampV1:
    def __init__(self, run_dir):
        self.manifest_path = os.path.join(run_dir, "stamp_manifest.jsonl")

    def record(self, order_id, artifact_path):
        entry = {"order_id": order_id, "path": artifact_path, "status": "SUCCESS"}
        with open(self.manifest_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return True