class Gate:
    def validate(self, p): return {"verdict":"ALLOW"} if p and "|" in p else {"verdict":"BLOCK"}