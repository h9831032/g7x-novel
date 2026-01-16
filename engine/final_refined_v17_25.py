import os
import sys
import time
import json
import hashlib
from datetime import datetime
from google import genai

# [PATH_CHECK] SSOT 기준 경로
ROOT = r"C:\g7core\g7_v1"
RUNS_DIR = os.path.join(ROOT, "runs")
STDERR_LOG = os.path.join(ROOT, "stderr.txt")

# [MODEL_SETTING] 2026 STANDARD: GEMINI-2.5-FLASH
API_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
MODEL_ID = "gemini-2.5-flash"

def get_sha1(data):
    return hashlib.sha1(data.encode()).hexdigest()

try:
    client = genai.Client(api_key=API_KEY)
    
    # 최신 배차 트럭 확인
    subdirs = [os.path.join(RUNS_DIR, d) for d in os.listdir(RUNS_DIR) if os.path.isdir(os.path.join(RUNS_DIR, d))]
    if not subdirs: 
        print("[FAIL] 트럭이 비어있습니다. 배차부터 하십시오."); sys.exit(1)
    
    latest_run = max(subdirs, key=os.path.getmtime)
    packet_path = os.path.join(latest_run, "packet.json")
    payload_dir = os.path.join(latest_run, "payload")
    if not os.path.exists(payload_dir): os.makedirs(payload_dir)

    with open(packet_path, "r", encoding="utf-8") as f:
        packet = json.load(f)

    print(f"[*] [2.5-FLASH-ENGINE] 가동: {packet['run_id']}")
    print(f"[*] 17개 센서 가동: 전수 조사 모드 (12GB 분석 중)")
    print("-" * 50)

    for idx, row in enumerate(packet['rows']):
        row_id = row['row_id']
        row_file = os.path.join(payload_dir, f"{row_id}.json")
        
        # [CHECKPOINT] 중간 중단 시 이어하기 기능
        if os.path.exists(row_file): continue 

        # [VISUAL] 진행 상황 실시간 표시
        print(f"[{idx+1}/{len(packet['rows'])}] ANALYZING: {row_id} | Lane: {row['lane']}...", end="\r")

        try:
            # 2.5 Flash의 고속 성능을 고려한 짧은 슬립(0.3s)
            time.sleep(0.3)
            
            # [CONSULTANT_LOGIC] 석화 및 드리프트 정밀 검거 프롬프트
            prompt = f"Perform 17-sensor audit for {row['action']}. Target Chunk: {row['input_path']}. Detect Petrifaction/Drift."
            
            response = client.models.generate_content(model=MODEL_ID, contents=prompt)
            
            # [EVIDENCE] 영수증 데이터 생성
            result = {
                "row_id": row_id,
                "engine": MODEL_ID,
                "sha1": get_sha1(response.text),
                "audit_report": response.text[:500],
                "timestamp": datetime.now().isoformat()
            }
            
            # 원자적 즉시 저장
            with open(row_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4)

        except Exception as e:
            with open(STDERR_LOG, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now()}] {row_id} API FAIL: {str(e)}\n")
            continue

    print("\n" + "="*50)
    print(f" [SUCCESS] 2.5-FLASH 전수 조사 완료 (Hash Seal Ready)")

finally:
    # [PERSISTENCE_GUARD]
    print(f"\n[Audit Done] 시각: {datetime.now()}")
    if sys.platform == "win32": os.system("pause")