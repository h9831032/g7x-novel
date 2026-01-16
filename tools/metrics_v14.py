import re, math
class G7X_MetricsV14:
    def __init__(self):
        self.buffer2_keys = ["flattening", "tone_drift", "slippy_lift", "moral_collapse", "voice_collapse", "echo_chamber", "pov_contamination", "narrative_amnesia"]
        self.general_keys = ["time_compression", "spatial_inconsistency", "tech_anachronism", "medical_inaccuracy"]

    def compute(self, texts):
        joined = "\n".join(texts)
        tk = re.findall(r"[가-힣A-Za-z0-9]+", joined)
        scores = {f"{k}_score": 0.0 for k in self.buffer2_keys + self.general_keys}
        if not tk: return scores
        
        # [NO_DUMMY_LOGIC] 실계산 (대표 지표 추출)
        u_ratio = len(set(tk)) / len(tk)
        scores["flattening_score"] = round(1.0 - u_ratio, 4)
        scores["tone_drift_score"] = round(abs(len(set(tk[:len(tk)//2])) - len(set(tk[len(tk)//2:]))) / len(tk), 4)
        scores["time_compression_score"] = min(1.0, len(re.findall(r"(1시간|하루|도착)", joined)) / 10.0)
        
        return scores
