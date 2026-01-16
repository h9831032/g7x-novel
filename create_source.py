import json
import os

root = r"C:\g7core\g7_v1"
target_path = os.path.join(root, "mission_catalog_phase3_REAL.jsonl")

# 지시서 규격에 따른 120개 미션 원천 데이터
with open(target_path, 'w', encoding='utf-8') as f:
    for i in range(1, 121):
        m_id = f"M{i:03d}"
        data = {
            "mission_id": m_id,
            "title": f"PHASE3_MISSION_UNIT_{m_id}",
            "objective": f"Execute strategic system audit and code analysis for node {m_id}. Ensure all evidence packs are generated.",
            "stamp_key": f"STAMP_{m_id}"
        }
        # 한 줄에 하나씩 JSON 기록 (JSONL 규격)
        f.write(json.dumps(data) + "\n")

print(f">>> [SUCCESS] Source file created: {target_path}")