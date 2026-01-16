import json

class ExceptionPackV1:
    def __init__(self):
        # [P1-035] ESSENTIAL_EXCEPTIONS (20 Keys) [cite: 2026-01-02]
        self.exceptions = {
            "EX_01_WORLD_SETTING": {"weight": 0.5, "desc": "세계관 고유 설정"},
            "EX_02_CHARACTER_VOICE": {"weight": 0.7, "desc": "캐릭터 특화 말투"},
            "EX_03_INTENTIONAL_REPETITION": {"weight": 0.3, "desc": "의도적 강조"},
            "EX_20_GENRE_CONVENTION": {"weight": 0.8, "desc": "장르적 관습"}
        }

    def apply_exceptions(self, raw_results, context=None):
        # [P1-037, 041] ExceptionApplicator: 리스크 감쇄 로직 [cite: 2026-01-02]
        risk_before = raw_results.get("stagnation_score", 0.0)
        applied_keys = []
        
        # 예시: 의도적 반복 감지 시 가중치 감쇄
        if context and context.get("is_emphasis", False):
            applied_keys.append("EX_03_INTENTIONAL_REPETITION")
            
        reduction_factor = 1.0
        for key in applied_keys:
            reduction_factor *= self.exceptions[key]["weight"]
            
        return {
            "exception_applied": len(applied_keys) > 0,
            "exception_keys": applied_keys,
            "risk_before": risk_before,
            "risk_after": round(risk_before * reduction_factor, 4)
        }
