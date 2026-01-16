import os
import json

root = r"C:\g7core\g7_v1"
catalog_path = os.path.join(root, "engine", "work_catalog_v3.json")

# M001 ~ M120까지 120개 작업 지침 생성
full_missions = []
for i in range(1, 121):
    m_id = f"M{i:03d}"
    full_missions.append({
        "mission_id": m_id,
        "title": f"PHASE3_MISSION_{m_id}",
        "objective": f"Perform deep technical analysis and system state audit for task {m_id}.",
        "stamp_key": f"STAMP_{m_id}"
    })

os.makedirs(os.path.dirname(catalog_path), exist_ok=True)
with open(catalog_path, 'w', encoding='utf-8') as f:
    json.dump({"missions": full_missions}, f, indent=4)

print(f">>> [SUCCESS] Catalog recharged with 120 missions: {catalog_path}")