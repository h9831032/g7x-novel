import os, hashlib
class Verifier:
    def verify(self, p):
        if not os.path.exists(p): return {"status":"FAIL"}
        with open(p, "rb") as f: h = hashlib.sha1(f.read()).hexdigest()
        return {"status":"PASS", "sha1": h}