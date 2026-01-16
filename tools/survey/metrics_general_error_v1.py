import re
class GeneralErrorMetricsV1:
    def __init__(self):
        self.error_keys = ["time_compression", "spatial_inconsistency", "tech_anachronism", "medical_inaccuracy"]

    def compute(self, text):
        errors = {k: 0.0 for k in self.error_keys}
        if not text: return {"scores": errors}
        
        raw_counts = {
            "time_compression": len(re.findall(r"(10분|1시간|하루).{0,50}(서울|부산|도착)", text)),
            "tech_anachronism": len(re.findall(r"(스마트폰|유튜브|SNS|인터넷)", text)),
            "medical_inaccuracy": len(re.findall(r"(심폐소생술|수혈|마취제)", text))
        }
        for k, v in raw_counts.items():
            errors[k] = min(1.0, v/5.0)
        return {"scores": errors, "evidence": raw_counts}
