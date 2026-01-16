import os
import json
import urllib.request
import hashlib
import time
from datetime import datetime

# [MANDATE: ELITE_ARCHITECT_MODE]
# 1. NO_DUMMY_LOGIC: 실제 파일 경로에서 동적으로 로드
# 2. EVIDENCE_MANDATED_AUDIT: 모든 결과에 SHA1 해시 및 물리 경로 포함

API_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
MODEL = "gemini-2.0-flash-exp"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

CHUNKS_DIR = r"C:\g6core\g6_v24\data\umr\chunks"
RUN_ID = f"RUN_PY_MASS_{datetime.now().strftime('%H%M%S')}"
BASE_DIR = r"C:\g7core\g7_v1\runs"
PAYLOAD_DIR = os.path.join(BASE_DIR, RUN_ID, "payload")

def get_file_sha1(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()

def main():
    print(f">>> [START] Python Extraction Engine Activity: {RUN_ID}")
    
    # 1. 인프라 구축
    if not os.path.exists(PAYLOAD_DIR):
        os.makedirs(PAYLOAD_DIR, exist_ok=True)
    
    if not os.path.exists(CHUNKS_DIR):
        print(f"[FAIL] Chunks directory not found: {CHUNKS_DIR}")
        return

    # 2. 타겟 스캔 (DYNAMIC_LOAD_ONLY)
    files = [f for f in os.listdir(CHUNKS_DIR) if os.path.isfile(os.path.join(CHUNKS_DIR, f))]
    total = len(files)
    print(f">>> [SCAN] Total Files Identified: {total}")

    if total == 0:
        print("[FAIL] No files to process. System Exit.")
        return

    # 3. 양산 루프
    for idx, filename in enumerate(files, 1):
        file_path = os.path.join(CHUNKS_DIR, filename)
        print(f" [{idx}/{total}] Processing: {filename}...", end=" ", flush=True)

        try:
            # 원문 로드 (1500자 샘플링)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            text_short = content[:1500]

            # API 페이로드 구성
            prompt = f"Analyze this novel chunk for [Setting Error, Logic Drift, Petrification] and return ONLY a JSON array. Content: {text_short}"
            body = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            
            # API 요청 (urllib 사용으로 의존성 제거)
            req = urllib.request.Request(API_URL, data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                raw_text = res_data['candidates'][0]['content']['parts'][0]['text']
                
                # JSON 정제
                clean_json = raw_text.replace("```json", "").replace("```", "").strip()
                
            # 결과 저장 (EVIDENCE_OR_FAIL)
            row_id = f"{idx:03d}"
            save_path = os.path.join(PAYLOAD_DIR, f"row_{row_id}.json")
            
            result_obj = {
                "row_id": idx,
                "source_file": filename,
                "analysis": json.loads(clean_json) if clean_json.startswith('[') else clean_json,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(result_obj, f, indent=2, ensure_ascii=False)
            
            # 해시 영수증 출력
            file_hash = get_file_sha1(save_path)
            print(f"-> [OK] (SHA1: {file_hash[:8]}...)")
            
            # API Rate Limit 방어
            time.sleep(1)

        except Exception as e:
            print(f"-> [FAIL] {str(e)}")

    print("\n" + "="*50)
    print(f" [COMPLETE] Mass Extraction Finished.")
    print(f" Output: {PAYLOAD_DIR}")
    print("="*50)
    input("\nAudit Done. Press Enter to Finalize (PERSISTENCE_GUARD)")

if __name__ == "__main__":
    main()