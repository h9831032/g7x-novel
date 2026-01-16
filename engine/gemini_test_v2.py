# [MANDATE] ELITE_ARCHITECT_MODE: NO_DUMMY_LOGIC
import os
import sys
import time
import json
from datetime import datetime
from google import genai  # 최신 라이브러리로 교체

# ==========================================
# [PATH_VERIFICATION] 
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
ROOT_DIR = os.path.dirname(BASE_DIR) # C:\g7core\g7_v1

AUDIT_LOG = os.path.join(ROOT_DIR, "audit_receipt.json")
STDERR_LOG = os.path.join(ROOT_DIR, "stderr.txt")

# ==========================================
# CONFIGURATION (Latest SDK 2.0 Standard)
# ==========================================
API_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
MODEL_ID = "gemini-2.0-flash-exp" # 최신 SDK는 'models/' 접두사 생략 가능

def fail_fast(msg):
    with open(STDERR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(f"\n\033[31m[CRITICAL FAILURE] {msg}\033[0m")
    os.system("pause")
    sys.exit(1)

# ==========================================
# NEW ENGINE (GenAI SDK 2.0)
# ==========================================
try:
    print(f"[*] Root: {ROOT_DIR}")
    
    # 신형 클라이언트 초기화
    client = genai.Client(api_key=API_KEY)
    
    start_ts = time.perf_counter()
    # 신형 호출 문법 (models.generate)
    response = client.models.generate_content(
        model=MODEL_ID,
        contents="SYSTEM_CHECK: Respond only with 'V2_READY'"
    )
    latency = time.perf_counter() - start_ts

    # 영수증 발행 (가라 아님 증명)
    receipt = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sdk_version": "genai-2.0",
        "latency": f"{latency:.4f}s",
        "result": response.text.strip()
    }

    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=4)

    print("\n" + "="*50)
    print(f" [SUCCESS] 신형 SDK 영수증 발행 완료")
    print(f" - 위치: {AUDIT_LOG}")
    print(f" - 응답: {receipt['result']}")
    print(f" - 속도: {receipt['latency']}")
    print("="*50 + "\n")

except Exception as e:
    fail_fast(f"SDK V2 실행 실패: {str(e)}")

finally:
    # [PERSISTENCE_GUARD]
    print(f"\n[Audit Done] {datetime.now()}")
    if sys.platform == "win32":
        os.system("pause")