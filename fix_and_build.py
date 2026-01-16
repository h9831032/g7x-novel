import json
import os
import sys

def fix_and_build():
    root = r"C:\g7core\g7_v1"
    plugin_dir = os.path.join(root, "plugins")
    os.makedirs(plugin_dir, exist_ok=True)
    
    # 1. factory_600.py 플러그인 파일 강제 생성
    factory_code = r'''
import json
import os

def run_plugin_logic():
    root = r"C:\g7core\g7_v1"
    gpt_order_path = os.path.join(root, "GPTORDER")
    os.makedirs(gpt_order_path, exist_ok=True)

    print(f">>> [FACTORY] Starting 600-Round Magazine Production...")

    # Catalog V2
    catalog = []
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
        catalog.append(entry)
    
    cat_path = os.path.join(root, "mission_catalog_v2.json")
    with open(cat_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2)
    print(f">>> [FACTORY] Created Catalog V2: {cat_path}")

    # Orders C~G
    batches = [('C', 121, 241), ('D', 241, 361), ('E', 361, 481), ('F', 481, 601), ('G', 601, 721)]
    queue_lines = []
    for label, start, end in batches:
        fname = f"REAL_MISSION_120_{label}.txt"
        fpath = os.path.join(gpt_order_path, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            for i in range(start, end):
                 f.write(f"M{i}\n")
        print(f">>> [FACTORY] Created Order {label}: {fpath}")
        queue_lines.append(fpath)

    # Queue
    q_path = os.path.join(gpt_order_path, "NIGHT_QUEUE_600.txt")
    with open(q_path, 'w', encoding='utf-8') as f:
        for line in queue_lines:
            f.write(line + "\n")
    print(f">>> [FACTORY] Created Queue: {q_path}")
    return True
'''
    factory_path = os.path.join(plugin_dir, "factory_600.py")
    with open(factory_path, 'w', encoding='utf-8') as f:
        f.write(factory_code)
    print(">>> [SETUP] factory_600.py created.")

    # 2. catalog.json 자동 등록
    catalog_path = os.path.join(plugin_dir, "catalog.json")
    if not os.path.exists(catalog_path):
        current_catalog = []
    else:
        with open(catalog_path, 'r', encoding='utf-8') as f:
            try:
                current_catalog = json.load(f)
            except:
                current_catalog = []
    
    # 중복 방지 후 추가
    entry = { "name": "factory_600", "path": "plugins/factory_600.py", "enabled": True }
    exists = any(p.get("name") == "factory_600" for p in current_catalog)
    if not exists:
        current_catalog.append(entry)
        with open(catalog_path, 'w', encoding='utf-8') as f:
            json.dump(current_catalog, f, indent=2)
        print(">>> [SETUP] catalog.json updated automatically.")
    else:
        print(">>> [SETUP] factory_600 already in catalog.")

    # 3. 플러그인 즉시 실행 (파일 생성 트리거)
    sys.path.append(plugin_dir)
    import factory_600
    factory_600.run_plugin_logic()
    print("\n>>> [COMPLETE] All files generated. You can run manager now.")

if __name__ == "__main__":
    fix_and_build()