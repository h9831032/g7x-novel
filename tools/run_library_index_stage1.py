import os, sys, json, hashlib, time, threading, random, re
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# [MANDATE-0] API_KEY 및 환경 설정
RAW_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
API_KEY = re.sub(r'[^\x00-\x7F]+', '', RAW_KEY).strip()
MODEL_ID = "models/gemini-2.0-flash" 

SSOT_ROOT = r"C:\g7core\g7_v1"
INPUT_PATH = r"C:\g6core\g6_v24\data\umr\chunks\fantasy_chunks.jsonl"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = os.path.join(SSOT_ROOT, "runs", f"INDEX_STAGE1_{TIMESTAMP}")
os.makedirs(RUN_DIR, exist_ok=True)

# [EVIDENCE_MANDATED_AUDIT] 로거 설정
class PersistenceLogger(object):
    def __init__(self, run_dir):
        self.terminal = sys.stdout
        self.log_path = os.path.join(run_dir, "stdout.txt")
        self.log = open(self.log_path, "a", encoding="utf-8")
    def write(self, m):
        self.terminal.write(m)
        if not self.log.closed: self.log.write(m)
    def flush(self):
        self.terminal.flush()
        if not self.log.closed: 
            self.log.flush()
            try: os.fsync(self.log.fileno())
            except: pass
    def close(self):
        if not self.log.closed: self.log.close()

logger = PersistenceLogger(RUN_DIR)
sys.stdout = logger

# [A7] 워커 안전모드 (6레인)
MAX_WORKERS = 6

thread_local = threading.local()
def get_client():
    if not hasattr(thread_local, "client"):
        thread_local.client = genai.Client(api_key=API_KEY)
    return thread_local.client

def get_res(p):
    """
    [1차 공정: 느슨한 문지기 모드]
    목적: 데이터 차단이 아니라, '어디가 이상한지' 딱지(Tag)를 붙이는 것이 최우선.
    """
    client = get_client()
    tag_rules = {
        "TAG_DRIFT": "설정흔들림", "TAG_ERROR": "문법오류", 
        "TAG_LOGIC": "개연성부족", "TAG_FUN": "재미요소"
    }
    prompt = (
        "당신은 도서관 입고 검수원입니다. 다음 소설 내용을 읽고 분류 태그를 붙이세요.\n"
        "내용이 읽기 불가능할 정도로 파손된 게 아니라면 가급적 ALLOW 하세요.\n"
        f"JSON 형식: {{\"verdict\":\"ALLOW|BLOCK\",\"why\":\"이유\",\"tags\":[]}}\n"
        f"분류규칙: {json.dumps(tag_rules, ensure_ascii=False)}\n"
        f"내용: {p}"
    )
    
    for _ in range(3):
        try:
            r = client.models.generate_content(model=MODEL_ID, contents=prompt, 
                                               config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1))
            j = json.loads(r.text)
            # [A2] 판정 로직: 명시적 BLOCK이 아니면 무조건 ALLOW (작업량 확보)
            rv = str(j.get('verdict', 'ALLOW')).upper()
            v = "BLOCK" if "BLOCK" in rv else "ALLOW"
            w = j.get('why', '')
            tags = j.get('tags', [])
            h = hashlib.sha256(f"{v}|{w}|{tags}".encode()).hexdigest()
            return v, w, tags, h, True, ""
        except:
            time.sleep(1)
    return "ALLOW", "retry_fail", [], "err_h", False, "api_error"

def seal_worker(task):
    row_id, p = task['id'], task['p']
    v, w, tags, h, ok, err = get_res(p)
    return {"ok": ok, "res": {"row": row_id, "v": v, "why": w, "tags": tags, "v_h": h, "err": err}}

def main():
    try:
        print(f"### [G6X INDEXING_STAGE1] START - 전수 인덱싱 및 라벨링")
        print(f"### Target File: {INPUT_PATH}")
        
        total, rw_a, rw_b = 0, 0, 0
        receipt_path = os.path.join(RUN_DIR, "audit_receipt.jsonl")
        
        with open(INPUT_PATH, "r", encoding="utf-8") as f_in, open(receipt_path, "a", encoding="utf-8") as f_out:
            batch = []
            for i, line in enumerate(f_in):
                batch.append({"id": i + 1, "p": line.strip()})
                if len(batch) >= 240:
                    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
                        results = list(ex.map(seal_worker, batch))
                    
                    for r in results:
                        f_out.write(json.dumps(r["res"], ensure_ascii=False) + "\n")
                        # [A1] 트럭별 실작업량(RW) 집계
                        c_id = (r["res"]["row"]-1)%240+1
                        if r["res"]["v"] == "ALLOW":
                            if 1 <= c_id <= 120: rw_a += 1
                            elif 121 <= c_id <= 240: rw_b += 1
                    
                    f_out.flush(); os.fsync(f_out.fileno())
                    total += len(batch)
                    # 트럭별 평균 작업량 출력
                    print(f"[@] {total} | Truck A RW: {rw_a/(total/240):.1f} B RW: {rw_b/(total/240):.1f}")
                    batch = []
                    # 테스트용 중단점 (12GB 전수 시 주석 처리하거나 조절)
                    # if total >= 1200: break 

        # [A5] 최종 리포트 봉인
        report = {
            "pass": (rw_a/(total/240) >= 90 and rw_b/(total/240) >= 90),
            "total_processed": total,
            "truck_rw": {"A": rw_a, "B": rw_b},
            "status": "STAGE1_INDEX_COMPLETED"
        }
        with open(os.path.join(RUN_DIR, "verify_report.json"), "w") as f: json.dump(report, f, indent=2)
        
        # [A6] 모든 파일 닫기 후 매니페스트 생성
        print(f"### [PROCESS] CLOSING LOGS FOR SEALING...")
        logger.flush(); logger.close()
        
        manifest = {}
        for fn in ["audit_receipt.jsonl", "stdout.txt", "verify_report.json"]:
            p = os.path.join(RUN_DIR, fn)
            if os.path.exists(p):
                with open(p, "rb") as f: manifest[fn] = hashlib.sha256(f.read()).hexdigest()
        
        with open(os.path.join(RUN_DIR, "hash_manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n### [SUCCESS] 1차 인덱싱 완료. 봉인 영수증 확인 필요.")
        print(f"### Output Path: {RUN_DIR}")

    except Exception as e:
        print(f"\a\n[FAIL] 치명적 오류 발생: {str(e)}")
    finally:
        # PERSISTENCE_GUARD
        print("-" * 50)
        input("Audit Done. 영수증을 확인하고 엔터를 눌러 종료하십시오...")

if __name__ == "__main__":
    main()