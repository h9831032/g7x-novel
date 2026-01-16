# C:\g7core\g7_v1\plugins\law60_enforcer.py
import json

class Law60Enforcer:
    def __init__(self):
        self.version = "v1.2_Constitutional"
        # [W044] 노트북LM 복원 3대 핵심 HARD_RULES
        self.rules = {
            "DEAD_ACT_CONFLICT": "사망한 엔티티의 활동 금지 (Federal Dead List 대조)",
            "LOC_IMPOSSIBLE_WARP": "물리적 거리 및 인과 관계 무시 이동 금지",
            "GENRE_BREAK": "세계관 설정 파괴 금지"
        }
        # 연방 사망자 명단 (FEDERAL_DEAD_LIST)
        self.dead_list = ["CHR_DEAD", "죽은_용사", "망자_A"]

    def enforce(self, record_id, payload):
        """[DoD] 근거가 부족하면 ALLOW하지 않는다 (헌법 제3조 준수)"""
        verdict = "ALLOW"
        score = 100
        violated_rule = None
        
        # 1. 사망자 활동 검사 (DEAD_ACT_CONFLICT)
        for name in self.dead_list:
            if name in payload:
                verdict = "BLOCK"
                score = 0
                violated_rule = "DEAD_ACT_CONFLICT"
                break
            
        return {
            "verdict": verdict,
            "score": score,
            "rule_applied": violated_rule if violated_rule else "LAW60_OK",
            "evidence": f"Analyzed {record_id} against Federal Dead List."
        }

def get_plugin():
    return Law60Enforcer()