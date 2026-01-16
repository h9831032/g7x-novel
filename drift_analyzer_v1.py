import os, sys, json, hashlib, threading
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# [MANDATE-0] API_KEY & 환경 고정
API_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
SSOT_ROOT = r"C:\g7core\g7_v1"
INPUT_PATH = r"C:\g6core\g6_v24\data\umr\chunks\fantasy_chunks.jsonl"
RUN_DIR = os.path.join(SSOT_ROOT, "runs", "DIAG_SESSION")
os.makedirs(RUN_DIR, exist_ok=True)

# [DIAG_LIMIT] 형님 오더: 센티넬 급 20개만 정밀 샘플링
DIAG_LIMIT = 20 

def analyze_drift(p):
    client = genai.Client(api_key=API_KEY)
    config = types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
    prompt = "Return JSON only. Schema: {\"verdict\":\"ALLOW|BLOCK\",\"why\":\"short\"}\nPayload: " + p

    try:
        # 동일 페이로드에 대해 2회 연속 호출하여 일관성 검증
        r1 = client.models.generate_content(model="gemini-2.5-flash", contents=prompt, config=config)
        r2 = client.models.generate_content(model="gemini-2.5-flash", contents=prompt, config=config)
        
        j1 = json.loads(r1.text)
        j2 = json.loads(r2.text)
        
        v1, v2 = j1.get("verdict"), j2.get("verdict")
        w1, w2 = j1.get("why"), j2.get("why")
        
        # [TRIAGE_LOGIC] 드리프트 종류별 분해
        d_type = "NONE"
        if v1 != v2: 
            d_type = "VERDICT_DRIFT" # 판정 번복 (치명적)
        elif w1 != w2: 
            d_type = "EXPLAIN_DRIFT" # 설명 흔들림 (경고/무시가능)
        
        return {"ok": True, "v1": v1, "v2": v2, "type": d_type, "p": p[:50]}
    except Exception as e:
        return {"ok": False, "type": "SCHEMA_ERROR", "err": str(e)}

def main():
    print(f"\n" + "="*60)
    print(f" [!] MANDATE: DRIFT_TRIAGE_MODE")
    print(f" [!] GOAL: 분해를 통해 봉인 가능한 구멍(Gap) 찾기")
    print(f" [!] ANALYZING FIRST {DIAG_LIMIT} CHUNKS...")
    print("="*60 + "\n")

    chunks = []
    if not os.path.exists(INPUT_PATH):
        print(f"[FAIL] Path missing: {INPUT_PATH}"); sys.exit(2)
        
    with open(INPUT_PATH, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if len(line.strip()) >= 500: chunks.append(line.strip())
            if len(chunks) >= DIAG_LIMIT: break

    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(tqdm(ex.map(analyze_drift, chunks), total=len(chunks), desc="TRIAGING"))

    # 통계 보고
    stats = {"VERDICT_DRIFT": 0, "EXPLAIN_DRIFT": 0, "SCHEMA_ERROR": 0, "NONE": 0}
    for r in results: stats[r['type']] += 1

    print(f"\n" + "="*60)
    print(f" [DIAG_REPORT] N={len(results)}")
    print(f" 1. VERDICT_DRIFT (판정번복): {stats['VERDICT_DRIFT']} 건 -> 봉인 불가 원인")
    print(f" 2. EXPLAIN_DRIFT (설명흔들): {stats['EXPLAIN_DRIFT']} 건 -> 무시가능 범위")
    print(f" 3. SCHEMA_ERROR  (규격오류): {stats['SCHEMA_ERROR']} 건 -> 시스템 결함")
    print(f" 4. STABLE        (완전정상): {stats['NONE']} 건")
    print("="*60)
    
    # 리딩 결론 도출 보조
    if stats['EXPLAIN_DRIFT'] > 0 and stats['VERDICT_DRIFT'] == 0:
        print("\n [리딩권고] 'why'만 흔들리고 있습니다. 해시에서 'why'를 제외하면 즉시 봉인 가능합니다.")
    elif stats['VERDICT_DRIFT'] > 0:
        print(f"\n [리딩권고] 판정 자체가 흔들리는 {stats['VERDICT_DRIFT']}건에 대해 '다수결(Voting)' 도입이 시급합니다.")

if __name__ == "__main__":
    main()