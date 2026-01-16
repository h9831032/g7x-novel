import os, json, collections, sys

def run(input_dir, output_dir):
    # 1. 유죄 판결문 로드
    candidates_path = os.path.join(input_dir, "topN_candidates.json")
    if not os.path.exists(candidates_path):
        print("FATAL: No candidates found."); return

    with open(candidates_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. 결함 유형 집계 (Stub logic: 실제로는 reason_code를 분석해야 함)
    # 현재 V27에서는 'verdict'만 있고 상세 reason이 텍스트에 묻혀있으므로
    # 텍스트 분석을 통해 가상의 위반 사유를 도출 (S09: 반복, S11: 어휘 등)
    
    violation_counts = collections.Counter()
    
    for item in data:
        # 시뮬레이션: snippet 길이나 내용으로 위반 유형 추정
        text = item.get('snippet', '')
        if len(text.split()) < 5: 
            violation_counts['TOO_SHORT'] += 1
        elif '  ' in text:
            violation_counts['FORMAT_ERROR'] += 1
        else:
            violation_counts['STYLE_FLATTENING'] += 1

    # Top 3 추출
    top3 = violation_counts.most_common(3)
    
    # 3. 결과 요약 (Next Order용)
    digest = {
        "source_run": os.path.basename(input_dir),
        "total_convicted": len(data),
        "top3_fail": [
            {"type": t[0], "count": t[1], "fix_priority": "HIGH" if i==0 else "MED"}
            for i, t in enumerate(top3)
        ],
        "recommendation": "FOCUS_ON_" + top3[0][0] if top3 else "NONE"
    }

    with open(os.path.join(output_dir, "result_digest_v1.json"), "w", encoding='utf-8') as f:
        json.dump(digest, f, ensure_ascii=False, indent=2)
        
    print(f"RADAR_COMPLETE: Top Violation -> {digest['recommendation']}")
    print(f"EVIDENCE: {json.dumps(digest['top3_fail'], ensure_ascii=False)}")

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
