import os
import json

def init_full_catalog():
    root = r"C:\g7core\g7_v1"
    catalog_path = os.path.join(root, "engine", "work_catalog_v1.json")
    os.makedirs(os.path.dirname(catalog_path), exist_ok=True)

    catalog = []
    
    # 1. CORE 핵심 12개
    core_tasks = [
        ("BASIC_ENGINE_WELD_001", "Gate(스키마/필수필드) 메인 시작부 강제", "main/gate.py"),
        ("BASIC_ENGINE_WELD_002", "Verifier(RAW/sha1 존재 검사)", "main/verifier.py"),
        ("BASIC_ENGINE_WELD_003", "BlackBox(START/END + sha1)", "engine/blackbox.py"),
        ("BASIC_ENGINE_WELD_004", "StampManifest(work_id->raw_sha1)", "engine/stamp.py"),
        ("BASIC_ENGINE_WELD_005", "VerifyReport(가라 탐지 로직)", "main/report.py"),
        ("BASIC_ENGINE_WELD_006", "FinalAudit(FAIL_BOX 라우팅)", "main/audit.py"),
        ("COST_GUARD_001", "REAL 호출 전 상한/연속FAIL3 STOP", "engine/guard.py"),
        ("ANTI_TURBO_001", "동일 초 몰림 탐지 및 강제 FAIL", "engine/anti_turbo.py"),
        ("ORDER_LOCK_001", "GPTORDER_ONLY 입력 봉인", "engine/lock.py"),
        ("RUN_WELD_001", "run.ps1 stdout/stderr 저장 강제", "tools/run_stable.ps1"),
        ("FAIL_BOX_001", "실패 RUN 즉시 격리 처리", "engine/fail_box.py"),
        ("SMOKE3_PACK_001", "SMOKE3 전용 3건 시나리오 빌드", "tools/make_smoke3.ps1")
    ]
    for cid, obj, out in core_tasks:
        catalog.append({"id": cid, "objective": obj, "outputs": out, "acceptance": "file_exists"})

    # 2. REAL 240개 (A120 + B120) 전량 등록
    for i in range(1, 241):
        catalog.append({
            "id": f"REAL_{i:03d}",
            "objective": f"G7X 시스템 모듈 {i:03d}단계 코드 정밀 패치",
            "outputs": f"src/module_{i:03d}.py",
            "acceptance": "file_exists"
        })
    
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=4)

    # 3. SMOKE3 주문서 재생성
    with open(os.path.join(root, "GPTORDER", "SMOKE3.txt"), "w", encoding="utf-8") as f:
        f.write("TASK_V2|payload=BASIC_ENGINE_WELD_001\nTASK_V2|payload=BASIC_ENGINE_WELD_002\nTASK_V2|payload=BASIC_ENGINE_WELD_003\n")

    print(f"   G7X_MSG: [SUCCESS] 252개 전체 카탈로그 및 SMOKE3 주문서 복구 완료.")

if __name__ == "__main__":
    init_full_catalog()