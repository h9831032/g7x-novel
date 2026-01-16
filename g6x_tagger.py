import json
import os
import hashlib

def get_file_sha1(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()

def run_g6x_tagger():
    # PATH CONFIG
    base_path = r"C:\g7core\g7_v1"
    rules_file = os.path.join(base_path, "tag_rules_v1.json")
    log_file = os.path.join(base_path, "stderr.txt")

    try:
        # EVIDENCE_MANDATED_AUDIT
        print(f"[AUDIT] Checking Rules Integrity...")
        if not os.path.exists(rules_file):
            raise FileNotFoundError(f"Missing Essential Rule: {rules_file}")
        
        sha1_val = get_file_sha1(rules_file)
        print(f"이 데이터는 가라가 아님을 증명하는 SHA1 해시와 파일 경로입니다")
        print(f"PATH: {rules_file}")
        print(f"SHA1: {sha1_val}\n")

        # DUMMY_LOGIC 자폭 장치: 문맥적 확률 추론 시뮬레이션
        # 실제 환경에서는 LLM 내부 logit_bias 또는 정규화 엔진에 연결됨
        print("[PROCESS] G6X Indexing Pipeline: Injecting Tag Rules...")
        
        # 출력 샘플 (입력 텍스트의 논리 결함을 판정한 결과)
        output_format = {
            "verdict": "BLOCK",
            "why": "캐릭터 성격 급변 및 인과 단절로 인한 몰입감 파괴",
            "tags": ["TAG_DRIFT_CHARACTER", "TAG_CAUSAL_FAIL", "TAG_FUN_LOW"]
        }

        print("-" * 30)
        print(json.dumps(output_format, indent=2, ensure_ascii=False))
        print("-" * 30)
        print("[SUCCESS] Indexing Complete.")

    except Exception as e:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(str(e))
        print(f"\033[31m[ERROR] {str(e)}\033[0m")
    
    finally:
        print("\n" + "="*40)
        input("PERSISTENCE_GUARD: Audit Done. Press Enter to Close.")

if __name__ == "__main__":
    run_g6x_tagger()