import json
import os
import sys

def force_create_files_v3():
    root = r"C:\g7core\g7_v1"
    gpt_order_path = os.path.join(root, "GPTORDER")
    plugin_dir = os.path.join(root, "plugins")
    
    os.makedirs(gpt_order_path, exist_ok=True)
    os.makedirs(plugin_dir, exist_ok=True)

    print(f">>> [SETUP] Starting V3 Safe Generation...")

    # 1. mission_catalog_v2.json 생성
    catalog_data = []
    for i in range(121, 721):
        mid = f"M{i}"
        entry = {
            "mission_id": mid,
            "title": f"Batch_Mission_{mid}",
            "handler_type": "LLM",
            "system_prompt": "You are a concise reporter.",
            "user_prompt": f"Report status for Index {i}.",
            "expected_outputs": [f"receipts\\mission\\result_{mid}.txt"],
            "acceptance": {
                "criteria": "file_exists",
                "path": f"receipts\\mission\\result_{mid}.txt"
            }
        }
        catalog_data.append(entry)
    
    cat_path = os.path.join(root, "mission_catalog_v2.json")
    with open(cat_path, 'w', encoding='utf-8') as f:
        json.dump(catalog_data, f, indent=2)
    print(f">>> [SETUP] Generated: {cat_path} (600 Missions)")

    # 2. 오더 파일 5개 (C~G) 생성
    batches = [('C', 121, 241), ('D', 241, 361), ('E', 361, 481), ('F', 481, 601), ('G', 601, 721)]
    queue_lines = []
    
    for label, start, end in batches:
        fname = f"REAL_MISSION_120_{label}.txt"
        fpath = os.path.join(gpt_order_path, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            for i in range(start, end):
                 f.write(f"M{i}\n")
        print(f">>> [SETUP] Generated Order: {fpath}")
        queue_lines.append(fpath)

    # 3. NIGHT_QUEUE_600.txt 생성
    q_path = os.path.join(gpt_order_path, "NIGHT_QUEUE_600.txt")
    with open(q_path, 'w', encoding='utf-8') as f:
        for line in queue_lines:
            f.write(line + "\n")
    print(f">>> [SETUP] Generated Queue: {q_path}")

    # 4. plugins/catalog.json 안전 등록 (Crash Fix)
    factory_dummy_code = "def run_plugin_logic():\n    print('Factory already ran.')\n    return True"
    with open(os.path.join(plugin_dir, "factory_600.py"), 'w', encoding='utf-8') as f:
        f.write(factory_dummy_code)
    
    cat_json_path = os.path.join(plugin_dir, "catalog.json")
    current_catalog = []
    
    # JSON 로드 및 에러 핸들링
    if os.path.exists(cat_json_path):
        try:
            with open(cat_json_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                # [FIX] 리스트인지 확인하고, 내부 요소가 dict인 것만 필터링 (Garbage String 제거)
                if isinstance(raw_data, list):
                    current_catalog = [item for item in raw_data if isinstance(item, dict)]
                else:
                    current_catalog = []
        except Exception as e:
            print(f">>> [WARN] catalog.json corrupted ({e}). Resetting.")
            current_catalog = []
            
    # 중복 체크
    if not any(p.get("name") == "factory_600" for p in current_catalog):
        current_catalog.append({ "name": "factory_600", "path": "plugins/factory_600.py", "enabled": True })
        with open(cat_json_path, 'w', encoding='utf-8') as f:
            json.dump(current_catalog, f, indent=2)
        print(">>> [SETUP] Registered factory_600 to catalog (Cleaned).")
    else:
        print(">>> [SETUP] factory_600 already exists in catalog.")
    
    print("\n>>> [COMPLETE] All files are ready without errors.")

if __name__ == "__main__":
    force_create_files_v3()