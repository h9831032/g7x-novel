import os, sys, json, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai

MODEL_NAME = "gemini-2.5-flash"
MAX_WORKERS = 2
progress_lock = threading.Lock()
completed_count = 0

def execute_task(task, res_dir, api_key, total_tasks, truck_source_dir):
    global completed_count
    client = genai.Client(api_key=api_key.strip())
    task_id = task['row_id']
    output_file = os.path.join(res_dir, f"task_{task_id}.json")
    
    # [SKIP] 이미 완공된 72개는 건너뛰고 73번부터 시작
    if os.path.exists(output_file):
        with progress_lock:
            completed_count += 1
        return True

    # [FORCE_PATH] 지시서의 가라 경로 무시, 실제 트럭 소스 폴더에서 강제 매칭
    file_name = f"source_{task_id}.txt" # 예: source_F_001.txt
    actual_path = os.path.join(truck_source_dir, file_name)

    if not os.path.exists(actual_path):
        # 만약 이름 형식이 다를 경우를 대비한 2차 탐색 (F_001.txt 등)
        actual_path = os.path.join(truck_source_dir, f"{task_id}.txt")
        if not os.path.exists(actual_path):
            print(f"!!! [NOT_FOUND] {task_id} 소스 실종: {actual_path}")
            return False

    try:
        with open(actual_path, "r", encoding='utf-8') as f:
            content = f.read()

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"너는 LAW60 제2조 설계 감리원이다. 다음 원고의 공간적 모순을 정밀 판정하라:\n\n{content}"
        )
        
        result = {"status": "SUCCESS", "output": response.text, "model": MODEL_NAME}
        with open(output_file, "w", encoding='utf-8') as out:
            json.dump(result, out, indent=4, ensure_ascii=False)
        
        with progress_lock:
            completed_count += 1
            print(f">>> [PROGRESS] {completed_count}/{total_tasks} | 완공: task_{task_id}")
        return True
    except Exception as e:
        print(f"!!! [RETRY] Task {task_id} 에러: {str(e)}")
        time.sleep(2)
        return False

def run_factory(truck_id, run_root):
    truck_path = os.path.join(run_root, f"truck{truck_id}")
    res_dir = os.path.join(truck_path, "FINAL_RESULTS")
    # [REAL_SOURCE] 트럭 내부에 소스가 있다고 가정 (72발 성공의 근거)
    truck_source_dir = os.path.join(truck_path, "source") 
    
    if not os.path.exists(truck_source_dir):
        # 경로가 다를 경우 G7X 표준 경로 시도
        truck_source_dir = os.path.join(run_root, "source", f"truck{truck_id}")

    os.makedirs(res_dir, exist_ok=True)
    api_key = os.getenv("GEMINI_API_KEY")
    
    tasks = []
    for i in range(1, 21):
        p = os.path.join(truck_path, f"bundle_{i:02d}", "bundle_packet.jsonl")
        if os.path.exists(p):
            with open(p, "r", encoding='utf-8') as f:
                tasks.extend([json.loads(line) for line in f])

    total_tasks = len(tasks)
    print(f"--- [FACTORY_RE-START] 대상: {total_tasks}개 | 엔진: {MODEL_NAME} ---")
    print(f"--- [SOURCE_PATH] {truck_source_dir} 에서 원료 공급 중 ---")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(execute_task, t, res_dir, api_key, total_tasks, truck_source_dir): t for t in tasks}
        for future in as_completed(futures):
            future.result()

if __name__ == "__main__":
    run_factory(sys.argv[1], sys.argv[2])