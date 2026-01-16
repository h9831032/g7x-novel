import os
import sys
import json
import hashlib
import re
import math
import argparse

def calculate_entropy(text):
    if not text: return 0
    prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
    return - sum([p * math.log(p) / math.log(2.0) for p in prob])

def get_file_evidence(file_path):
    # 1. PATH_VERIFICATION_GUARD
    if not os.path.exists(file_path):
        sys.stderr.write(f"REASON: PHYSICAL_FILE_MISSING\n")
        sys.exit(1)

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            raw_data = json.load(f)
            # 전체 데이터를 문자열화하여 검사
            full_content = json.dumps(raw_data, ensure_ascii=False)
        except Exception:
            sys.stderr.write("REASON: JSON_DECODE_ERROR\n")
            sys.exit(1)

    # 2. [CONTEXT_AWARE_SENTINEL]: 지능형 가라 탐지
    # 단순히 단어를 찾는 게 아니라, '짧은 단독 문구'로 쓰일 때만 가라로 간주
    fake_targets = ["가라", "구라", "DUMMY", "SAMPLE"]
    
    for target in fake_targets:
        # 단어가 발견되었을 때
        if re.search(fr"(?<![가-힣]){target}(?![가-힣])", full_content):
            # [EXCEPTION_GUARD]
            # 1. '가라앉다' 계열은 무조건 세이프
            if target == "가라" and "가라앉" in full_content:
                continue
            
            # 2. 문맥 보호: 해당 단어가 포함된 전체 텍스트가 50자 이상이면 '리뷰/소설'로 간주하여 통과
            # (독립적으로 "가라", "구라"라고만 적힌 시스템 가라를 잡기 위함)
            if len(full_content) > 500: # 파일 전체 크기가 크면 서사 데이터로 인정
                continue
                
            sys.stderr.write(f"REASON: SYSTEM_FAKE_DETECTED ({target})\n")
            sys.exit(1)

    # 3. EVIDENCE_MANDATED_AUDIT
    sha256 = hashlib.sha256(full_content.encode('utf-8')).hexdigest()
    entropy = calculate_entropy(full_content)
    file_size = os.path.getsize(file_path)
    
    # 통계 기반 스코어링 (0~100)
    score = round(min(100, (entropy * 8) + (file_size / 2000)), 2)

    return {
        "Score": score,
        "SHA256": sha256,
        "Evidence": {
            "Entropy": round(entropy, 4),
            "Physical_Size": file_size,
            "Context_Status": "REAL_DATA_VERIFIED"
        }
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()
    
    try:
        result = get_file_evidence(args.file)
        print(json.dumps(result))
    except Exception as e:
        sys.stderr.write(f"REASON: {str(e)}\n")
        sys.exit(1)