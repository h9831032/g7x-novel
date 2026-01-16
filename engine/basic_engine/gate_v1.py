import re
class GateV1:
    def validate(self, payload):
        if not payload or "|" not in payload: return {"verdict": "BLOCK"}
        if any(x in payload for x in ["", "MOCK_DATA"]): return {"verdict": "BLOCK"}
        return {"verdict": "ALLOW"}