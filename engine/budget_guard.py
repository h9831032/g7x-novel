import sys
class BudgetGuard:
    def check(self, u, s): return True if u > 0 else sys.exit(1)