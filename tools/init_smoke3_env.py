import os
import json

def init_env():
    root = r"C:\g7core\g7_v1"
    dirs = [
        "main", "engine", "tools", "GPTORDER", "runs", "output", "src"
    ]
    for d in dirs:
        os.makedirs(os.path.join(root, d), exist_ok=True)

    # 1. SMOKE3용 작업 카탈로그 (핵심 12선)
    catalog = [
        {"id": "BASIC_ENGINE_WELD_001", "objective": "Gate(스키마/필수필드) 메인 시작부 강제", "outputs": "main/gate.py", "acceptance": "class:GateExists"},
        {"id": "BASIC_ENGINE_WELD_002", "objective": "Verifier(RAW/sha1 존재 검사)", "outputs": "main/verifier.py", "acceptance": "function:verify_sha1"},
        {"id": "BASIC_ENGINE_WELD_003", "objective": "BlackBox(START/END + sha1)", "outputs": "engine/blackbox.py", "acceptance": "format:jsonl"},
        {"id": "BASIC_ENGINE_WELD_004", "objective": "StampManifest(work_id->raw_sha1)", "outputs": "engine/stamp.py", "acceptance": "file_exists"},
        {"id": "BASIC_ENGINE_WELD_005", "objective": "VerifyReport(가라 탐지 로직)", "outputs": "main/report.py", "acceptance": "logic:turbo_detect"},
        {"id": "BASIC_ENGINE_WELD_006", "objective": "FinalAudit(FAIL_BOX 라우팅)", "outputs": "main/audit.py", "acceptance": "dir:FAIL_BOX"},
        {"id": "COST_GUARD_001", "objective": "REAL 호출 전 상한/연속FAIL3 STOP", "outputs": "engine/guard.py", "acceptance": "logic:stop_limit"},
        {"id": "ANTI_TURBO_001", "objective": "동일 초 몰림 탐지 및 강제 FAIL", "outputs": "engine/anti_turbo.py", "acceptance": "logic:ts_diff"},
        {"id": "ORDER_LOCK_001", "objective": "GPTORDER_ONLY 입력 봉인", "outputs": "engine/lock.py", "acceptance": "file_exists"},
        {"id": "RUN_WELD_001", "objective": "run.ps1 stdout/stderr 저장 강제", "outputs": "tools/run_stable.ps1", "acceptance": "file_exists"},
        {"id": "FAIL_BOX_001", "objective": "실패 RUN 즉시 격리 처리", "outputs": "engine/fail_box.py", "acceptance": "dir:runs/FAIL_BOX"},
        {"id": "SMOKE3_PACK_001", "objective": "SMOKE3 전용 3건 시나리오 빌드", "outputs": "tools/make_smoke3.ps1", "acceptance": "file_exists"}
    ]
    
    with open(os.path.join(root, "engine", "work_catalog_v1.json"), "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=4)

    # 2. SMOKE3 주문서 생성 (3줄)
    with open(os.path.join(root, "GPTORDER", "SMOKE3.txt"), "w", encoding="utf-8") as f:
        f.write("TASK_V2|payload=BASIC_ENGINE_WELD_001\n")
        f.write("TASK_V2|payload=BASIC_ENGINE_WELD_002\n")
        f.write("TASK_V2|payload=BASIC_ENGINE_WELD_003\n")

    print(f"   G7X_MSG: [SUCCESS] SMOKE3 환경 초기화 완료.")

if __name__ == "__main__":
    init_env()