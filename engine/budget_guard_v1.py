# C:\g7core\g7_v1\engine\budget_guard.py
import sys

class BudgetGuard:
    def check(self, usage, sha1):
        # 1. 가라 감시: 토큰 0이면 즉시 종료
        if usage <= 0:
            print("!!! [FATAL] Zero usage detected. Gara Suspected.")
            sys.exit(1)
        return True