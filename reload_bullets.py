import os
import json

# 1. 루트 경로 설정
root = r"C:\g7core\g7_v1"

def reload_all():
    print(">>> [INIT] Starting full reload of 120 bullets...")

    # 2. 미션 카탈로그 120개 생성 (engine/mission_catalog_v1.json)
    catalog_dir = os.path.join(root, "engine")
    catalog_path = os.path.join(catalog_dir, "mission_catalog_v1.json")
    os.makedirs(catalog_dir, exist_ok=True)

    missions = []
    for i in range(1, 121):
        m_id = f"M{i:03d}"
        missions.append({
            "mission_id": m_id,
            "title": f"MISSION_{m_id}_STRATEGIC_ANALYSIS",
            "objective": f"Perform a deep system audit for task {m_id} and generate a technical summary.",
            "stamp_key": f"STAMP_{m_id}",
            "kind": "DEVLOG"
        })

    # [중요] 리스트 형태가 아닌 딕셔너리 하부의 "missions" 키로 저장
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump({"missions": missions}, f, indent=4)
    print(f">>> [OK] 120 Missions defined in: {catalog_path}")

    # 3. 주문서 120발 장전 (GPTORDER/REAL_MISSION_120_A.txt)
    order_dir = os.path.join(root, "GPTORDER")
    order_path = os.path.join(order_dir, "REAL_MISSION_120_A.txt")
    os.makedirs(order_dir, exist_ok=True)

    with open(order_path, 'w', encoding='utf-8') as f:
        for i in range(1, 121):
            # TASK_V3 규격 준수
            f.write(f"TASK_V3|mission=M{i:03d}\n")
    print(f">>> [OK] 120 Orders loaded in: {order_path}")

    print("-" * 50)
    print(">>> [READY] All bullets loaded. You can now run manager.py")
    print("-" * 50)

if __name__ == "__main__":
    reload_all()