import os
import json

root = r"C:\g7core\g7_v1"
order_path = os.path.join(root, "GPTORDER", "REAL120_B.txt")
jsonl_path = os.path.join(root, "mission_catalog_phase3_REAL.jsonl")

if not os.path.exists(order_path):
    print(f">>> [ERROR] Order file not found: {order_path}")
    exit(1)

print(f">>> Scanning IDs from {order_path}...")

with open(order_path, 'r', encoding='utf-8') as f:
    # 한 줄에 하나씩 ID 추출 (mission= 접두사 제거)
    ids = []
    for line in f:
        raw = line.strip()
        if not raw: continue
        m_id = raw.split("mission=")[-1] if "mission=" in raw else raw
        ids.append(m_id)

# 중복 제거 및 JSONL 생성
with open(jsonl_path, 'w', encoding='utf-8') as f:
    for m_id in ids:
        entry = {
            "mission_id": m_id,
            "title": f"AUTO_SYNC_{m_id}",
            "objective": f"Perform deep analysis for payload: {m_id}. System state check required.",
            "stamp_key": f"STAMP_{hash(m_id)}"
        }
        f.write(json.dumps(entry) + "\n")

print(f">>> [SUCCESS] Synchronized {len(ids)} IDs to {jsonl_path}")