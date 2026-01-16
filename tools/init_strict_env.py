import os, json

def init_strict_env():
    root = r'C:\g7core\g7_v1'
    dirs = ['main', 'engine', 'tools', 'GPTORDER', 'runs', 'output', 'src']
    for d in dirs: os.makedirs(os.path.join(root, d), exist_ok=True)

    # Strict Catalog (Routing Rules)
    catalog = [
        {'id': 'BASIC_ENGINE_WELD_001', 'objective': 'Gate/Schema Validation', 'outputs': 'main/gate.py'},
        {'id': 'BASIC_ENGINE_WELD_002', 'objective': 'Verifier Logic (SHA1)', 'outputs': 'main/verifier.py'},
        {'id': 'BASIC_ENGINE_WELD_003', 'objective': 'Blackbox Logging', 'outputs': 'engine/blackbox.py'}
    ]
    
    cat_path = os.path.join(root, 'engine', 'work_catalog_v1.json')
    with open(cat_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=4)

    # SMOKE3 Order
    with open(os.path.join(root, 'GPTORDER', 'SMOKE3.txt'), 'w', encoding='utf-8') as f:
        f.write('TASK_V2|payload=BASIC_ENGINE_WELD_001\n')
        f.write('TASK_V2|payload=BASIC_ENGINE_WELD_002\n')
        f.write('TASK_V2|payload=BASIC_ENGINE_WELD_003\n')

    print('[SUCCESS] Strict Environment & SMOKE3 Order Initialized.')

if __name__ == '__main__':
    init_strict_env()
