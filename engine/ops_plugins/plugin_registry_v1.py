import hashlib
import re
import math
from collections import Counter

class PHOENIX_PLUGINS:
    """ [질문.txt] 알고리즘 5대 축 플러그인 모음 [cite: 15, 22, 53] """

    @staticmethod
    def quick_scanner(payload):
        """ G01-G60 키워드/패턴 스캔 기반 위험도 산출 [cite: 22, 55] """
        risk = 0
        patterns = {
            r"순간이동|포탈|차원": 30, # 공간 게이트 [cite: 58]
            r"부활|죽었는데|살아나": 40, # 존재성 게이트 [cite: 26]
            r"회상|과거|기억": 20      # 시간 게이트 [cite: 56]
        }
        for pat, score in patterns.items():
            if re.search(pat, payload): risk += score
        return min(risk, 100)

    @staticmethod
    def semantic_fingerprint(text):
        """ blake2b 기반 중복 박멸 지문 생성 (64비트) [cite: 22, 116, 156] """
        return hashlib.blake2b(text.encode(), digest_size=8).hexdigest()

    @staticmethod
    def entropy_fun_score(text):
        """ 셰넌 엔트로피 기반 정보 밀도 및 재미 측정 [cite: 46, 126, 131] """
        if not text: return 0.0
        words = text.split()
        counts = Counter(words)
        probs = [c / len(words) for c in counts.values()]
        entropy = -sum(p * math.log2(p) for p in probs)
        return round(entropy, 4)

    @staticmethod
    def smart_router(risk_score):
        """ 위험도 기반 공정 분기 (GATE vs SENSOR) [cite: 15, 22] """
        return "GATE_FIRST" if risk_score >= 60 else "SENSOR_FIRST"

    @staticmethod
    def entity_state_flag(audit_json):
        """ 인물 상태 모순 및 복선 감지 플래그 추출 [cite: 40, 54, 87] """
        has_contradiction = len(audit_json.get("contradictions", [])) > 0
        is_foreshadowing = bool(audit_json.get("foreshadowing", False))
        return {
            "is_anomaly": has_contradiction and not is_foreshadowing, # 진짜 오류 [cite: 43]
            "is_setup": is_foreshadowing # 의도된 복선 [cite: 41]
        }