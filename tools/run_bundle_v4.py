import sys, os, json, time

# [V4.0] 6x20 전용 실행 엔진
# 기능: 매 번들 종료 시 state_pack.json 갱신 + BudgetGuard (상한 초과 시 자폭)

BUDGET_LIMIT = 50 # API 호출 상한 (예시: 50회 초과 시 중단)

def run_bundle(truck_id, bundle_idx, run_dir):
    bundle_path = os.path.join(run_dir, f"truck{truck_id}", f"bundle_{bundle_idx:02d}")
    state_file = os.path.join(run_dir, "state_pack.json")
    
    # BudgetGuard 체크
    current_calls = 0
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            state = json.load(f)
            current_calls = state.get("realcall_count", 0)
    
    if current_calls >= BUDGET_LIMIT:
        print(f"!!! [BUDGET_GUARD_TRIP] Limit {BUDGET_LIMIT} Exceeded. STOP.")
        sys.exit(3) # SSOT 규격 exitcode=3

    # 번들 작업 시뮬레이션 (실제로는 inner_engine 호출)
    print(f">>> [RUN] Truck {truck_id} | Bundle {bundle_idx} | Calls: {current_calls}")
    time.sleep(1) 
    
    # STATE_PACK 갱신 (영혼 보존)
    new_state = {
        "truck_id": truck_id,
        "bundle_idx": bundle_idx,
        "realcall_count": current_calls + 1, # 번들당 1회 호출 가정
        "last_update": time.ctime(),
        "status": "RUNNING"
    }
    with open(state_file, "w") as f:
        json.dump(new_state, f, indent=4)

if __name__ == "__main__":
    # 파워쉘에서 인자 전달: truck_id, bundle_idx, run_dir
    run_bundle(sys.argv[1], int(sys.argv[2]), sys.argv[3])