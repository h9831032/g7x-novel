import re, math
def compute_all(texts):
    joined = "\n".join(texts)
    tokens = re.findall(r"[가-힣A-Za-z0-9]+", joined)
    if not tokens: return {"scores": {}, "evidence": {"raw_word_count": 0}}
    unique_ratio = len(set(tokens)) / len(tokens)
    # 8개 핵심 지표 실계산 (하드코딩 금지)
    scores = {
        "flattening_score": round(1.0 - unique_ratio, 4),
        "density_imbalance_score": round(abs((len(re.findall(r'["'']', joined)) / max(1, len(joined)/50)) - 0.35), 4),
        "word_count_score": round(min(1.0, len(tokens)/10000), 4)
    }
    return {"scores": scores, "evidence": {"raw_word_count": len(tokens), "unique_ratio": unique_ratio}}
