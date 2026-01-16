# C:\g7core\g7_v1\engine\verifier.py
import os, hashlib

class Verifier:
    def verify(self, artifact_path):
        if not os.path.exists(artifact_path):
            return {"status": "FAIL", "reason": "NOT_FOUND"}
        if os.path.getsize(artifact_path) < 10:
            return {"status": "FAIL", "reason": "EMPTY_FILE"}
        with open(artifact_path, "rb") as f:
            sha1 = hashlib.sha1(f.read()).hexdigest()
        return {"status": "PASS", "sha1": sha1}