import math, re

class SensorPackV1:
    def __init__(self):
        # [P1-030] 지시서 기반 임계값 테이블 (Thresholds)
        self.thresholds = {
            "S09_REPEAT_LIMIT": 0.35,
            "S10_MIN_VARIANCE": 10.0,
            "DRIFT_BASE": 0.5
        }

    def get_s09_repetition(self, text):
        # [P1-026] S09 유지: 단어 반복률 계산 [cite: 2026-01-02]
        words = text.split()
        if not words: return 0.0
        return 1.0 - (len(set(words)) / len(words))

    def get_s10_variance(self, text):
        # [P1-027] S10 추가: 문장 길이 분산도 normalized [cite: 2026-01-02]
        sentences = re.split(r'[.!?]', text)
        lengths = [len(s.strip()) for s in sentences if len(s.strip()) > 0]
        if len(lengths) < 2: return 0.0
        mean = sum(lengths) / len(lengths)
        variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
        return min(variance / 100.0, 1.0) # 0~1 정규화

    def analyze_record(self, record_text):
        # [P1-024, 025] 14센서 수치 산출 (Deterministic Heuristics) [cite: 2026-01-02]
        s09 = self.get_s09_repetition(record_text)
        s10 = self.get_s10_variance(record_text)
        
        # S01~S14 범용 필드 (현재는 S09, S10 외 스텁 처리)
        results = {f"S{i:02d}": 0.0 for i in range(1, 15)}
        results["S09"] = round(s09, 4)
        results["S10"] = round(s10, 4)
        
        # [P1-029] Stagnation Score (정체 수치): 반복 높고 분산 낮을 때 상승
        stagnation = (s09 + (1.0 - s10)) / 2.0
        results["stagnation_score"] = round(stagnation, 4)
        results["drift_score"] = 0.0 # 후속 drift_pack 연동 예정
        
        return results

if __name__ == "__main__":
    # 단위 테스트 (Unit Test)
    test_text = "이것은 반복 반복 반복입니다. 문장이 아주 짧습니다. 하지만 이것은 반복입니다."
    pack = SensorPackV1()
    print(pack.analyze_record(test_text))
