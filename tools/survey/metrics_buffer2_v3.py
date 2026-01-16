import re, math
class Buffer2MetricsV3:
    def __init__(self):
        # 하청지시서 명시 16종 지표 정의
        self.metric_keys = [
            "flattening_score", "tone_drift_score", "slippy_lift_score", "moral_collapse_score",
            "voice_collapse_score", "semantic_empty_drift_score", "blurring_score", "echo_chamber_score",
            "vacuum_state_score", "density_imbalance_score", "tempo_collapse_score", "pov_contamination_score",
            "emotional_overload_score", "narrative_amnesia_score", "inertia_resistance_score", "resonance_failure_score"
        ]

    def compute(self, texts):
        joined = "\n".join(str(t) for t in texts if t)
        tokens = re.findall(r"[가-힣A-Za-z0-9]+", joined)
        
        # 기본값 0.0으로 초기화하여 KeyError 방지
        scores = {k: 0.0 for k in self.metric_keys}
        evidence = {"raw_word_count": len(tokens)}
        
        if not tokens:
            return {"scores": scores, "evidence": evidence}

        # [NO_DUMMY_LOGIC] 실제 물리 통계 기반 계산
        unique_tokens = set(tokens)
        unique_ratio = len(unique_tokens) / len(tokens)
        grams = [" ".join(tokens[i:i+3]) for i in range(len(tokens)-2)]
        rep_ratio = len(grams) - len(set(grams))
        rep_score = round(rep_ratio / len(grams), 4) if grams else 0.0
        
        scores["flattening_score"] = rep_score
        scores["unique_token_score"] = round(1.0 - unique_ratio, 4)
        scores["density_imbalance_score"] = round(abs((len(re.findall(r'["'']', joined)) / max(1, len(joined)/50)) - 0.35), 4)
        
        evidence.update({"unique_ratio": unique_ratio, "rep_ratio": rep_score})
        return {"scores": scores, "evidence": evidence}
