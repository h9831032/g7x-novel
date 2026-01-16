# C:\g7core\g7_v1\engine\budget_guard_v1.py
import sys

class BudgetGuardV1:
    def __init__(self, repeat_limit=3):
        self.history_hashes = set()
        self.repeat_limit = repeat_limit
        print(">>> [GUARD] Budget Police Active. (Block Missing Modules)", flush=True)

    def check(self, usage, sha1):
        if usage <= 0:
            print("!!! [STOP] Zero Usage Detected. Gara suspected.", flush=True)
            sys.exit(1)
        if sha1 in self.history_hashes:
            print(f"!!! [STOP] Duplicate Hash Detected: {sha1}", flush=True)
            sys.exit(1)
        self.history_hashes.add(sha1)
        return True