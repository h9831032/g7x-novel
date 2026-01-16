import sys, os, json
from logic.inner_engine_real_v1 import InnerEngineReal

# [V5.1] BudgetGuard 300 상향 + 실전 배선 통합
def run_bundle_v5(truck_id, bundle_idx, run_dir, calls_limit=300):
    truck_final_dir = os.path.join(run_dir, f"truck{truck_id}", "FINAL")
    os.makedirs(truck_final_dir, exist_ok=True)
    receipt_path = os.path.join(run_dir, "api_receipt.jsonl")
    
    # 1. BudgetGuard: API 영수증 라인 수 전수 조사
    current_calls = 0
    if os.path.exists(receipt_path):
        with open(receipt_path, "r") as f:
            current_calls = sum(1 for _ in f)
    
    if current_calls >= calls_limit:
        with open(os.path.join(truck_final_dir, "exitcode.txt"), "w") as f: f.write("3")
        print(f"!!! [BUDGET_GUARD_TRIP] STOP (Current: {current_calls})")
        sys.exit(3)

    # 2. 인증 및 엔진 로드
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: sys.exit(1)
    engine = InnerEngineReal(api_key=api_key)

    # 3. 번들 작업 실행 (6개 Task)
    bundle_path = os.path.join(run_dir, f"truck{truck_id}", f"bundle_{bundle_idx:02d}")
    results_dir = os.path.join(bundle_path, "results")
    os.makedirs(results_dir, exist_ok=True)

    with open(os.path.join(bundle_path, "bundle_packet.jsonl"), "r") as f:
        tasks = [json.loads(line) for line in f]

    done_ids = []
    for task in tasks:
        res = engine.execute(task)
        if res.get("api_used"):
            with open(receipt_path, "a") as f:
                f.write(json.dumps(res) + "\n")
        
        with open(os.path.join(results_dir, f"task_{task['row_id']}.json"), "w") as f:
            json.dump(res, f)
        done_ids.append(task['row_id'])

    # 4. State Pack 봉인
    state = {"run_id": "REAL", "truck_id": truck_id, "bundle_idx": bundle_idx, "done_task_ids": done_ids}
    with open(os.path.join(truck_final_dir, "state_pack.json"), "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    run_bundle_v5(sys.argv[1], int(sys.argv[2]), sys.argv[3])