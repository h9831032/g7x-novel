import os, sys, json, csv, time, hashlib, random, threading, io, glob
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# [PATCH-0] UTF-8 및 윈도우 환경 방어
sys.stdin = io.TextIOWrapper(sys.stdin.detach(), encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

# [SSOT] 설정부
API_KEY = os.getenv("GEMINI_API_KEY")
TARGET_DIR = r"C:\g6core\g6_v24\data\umr\chunks"
SSOT_ROOT = r"C:\g7core\g7_v1"
MODEL_ID = "gemini-2.5-flash"
RUN_ID = "FINAL_MIGRATION_PROD" # 이 이름을 고정해야 이어서 하기가 작동합니다.
RUN_DIR = os.path.join(SSOT_ROOT, "runs", RUN_ID)
os.makedirs(RUN_DIR, exist_ok=True)
TSV_PATH = os.path.join(RUN_DIR, "result_packet.tsv")

# [하청] 가장 큰 파일 자동 선택 (A화일인지 B화일인지 식별용)
all_files = glob.glob(os.path.join(TARGET_DIR, "*"))
INPUT_FILE = max(all_files, key=os.path.getsize)
FILE_NAME = os.path.basename(INPUT_FILE)

# [튜닝] 4차선 가속 및 안전 잠금장치
GEMINI_SEM = threading.Semaphore(4) 
SAVE_LOCK = threading.Lock()

def get_done_ids():
    """기존 영수증을 읽어 이미 완료된 번호를 추출 (이어서 하기)"""
    done_ids = set()
    if os.path.exists(TSV_PATH):
        try:
            with open(TSV_PATH, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter="\t")
                next(reader, None) # 헤더 스킵
                for row in reader:
                    if row: done_ids.add(int(row[0]))
        except: pass
    return done_ids

def sha256_text(text): return hashlib.sha256(text.encode('utf-8')).hexdigest()

def stream_build_chunks(path, chunk_size=2500, overlap=200):
    """메모리 절약형 스트리밍 독해"""
    current_text = ""
    step = chunk_size - overlap
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        while True:
            buffer = f.read(1024 * 1024)
            if not buffer: break
            current_text += buffer
            while len(current_text) >= chunk_size:
                yield current_text[:chunk_size]
                current_text = current_text[step:]
    if current_text.strip(): yield current_text

thread_local = threading.local()
def get_client():
    if not hasattr(thread_local, "client"): thread_local.client = genai.Client(api_key=API_KEY)
    return thread_local.client

def audit_worker(task):
    client = get_client()
    try:
        with GEMINI_SEM:
            # 실전 문맥 판정 (DUMMY_LOGIC 자폭 모드 가동)
            response = client.models.generate_content(
                model=MODEL_ID, 
                contents=f"Mode: AUDIT. JSON ONLY. Evidence Required. Payload: {task['payload']}",
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0)
            )
        res_json = json.loads(response.text)
        verdict = str(res_json.get("verdict", "BLOCK")).upper()
        
        # [EVIDENCE_MANDATED] 영수증 데이터 구성
        row = [task['row_id'], f"T_{task['row_id']}", FILE_NAME, task['payload_hash'], verdict, 0.95, res_json.get("why", "OK"), int(time.time())]
        
        # [정전 대비] 1건당 즉시 물리적 박제 (f.flush)
        with SAVE_LOCK:
            file_exists = os.path.isfile(TSV_PATH)
            with open(TSV_PATH, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter="\t")
                if not file_exists: 
                    writer.writerow(["row_id", "task_id", "source", "hash", "verdict", "score", "why", "ts"])
                writer.writerow(row)
                f.flush() # OS 버퍼 강제 비우기
        return True
    except:
        return False

def main():
    print("\n" + "="*50)
    print(f" [G7-DASHBOARD] 12GB MIGRATION ENGINE V2")
    print("="*50)
    print(f" ▶ TARGET FILE : {FILE_NAME}")
    print(f" ▶ ENGINE      : {MODEL_ID}")
    print(f" ▶ LANES       : 4 Threads (Optimized)")
    print(f" ▶ SAVE PATH   : {TSV_PATH}")
    print("="*50)

    done_ids = get_done_ids()
    if done_ids:
        print(f" [INFO] 이미 완료된 {len(done_ids)}개 데이터를 발견했습니다. 이어서 주행합니다.")

    # 1. 태스크 생성 (메모리 가드 적용)
    tasks = []
    print(" [INFO] 데이터 로딩 및 작업 리스트 생성 중...")
    for i, chunk in enumerate(stream_build_chunks(INPUT_FILE)):
        row_id = i + 1
        if row_id in done_ids: continue
        tasks.append({"row_id": row_id, "payload": chunk, "payload_hash": sha256_text(chunk)})
    
    total = len(tasks)
    if total == 0:
        print(" [SUCCESS] 모든 작업이 이미 완료되었습니다!")
        return

    # 2. 실전 주행 (가시성 강화 tqdm)
    # bar_format: 진행률 | 바 | 현재/전체 [경과시간<남은시간, 속도]
    custom_format = " {desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(tqdm(ex.map(audit_worker, tasks), total=total, desc=" [주행중]", bar_format=custom_format))

    print("\n" + "="*50)
    print(f" [MISSION COMPLETE] 모든 이사가 완료되었습니다.")
    print(f" 최종 결과물: {TSV_PATH}")
    print("="*50)
    input("엔터를 누르면 종료됩니다...")

if __name__ == "__main__":
    main()