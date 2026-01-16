import json, os, re
from datetime import datetime

def build_v3():
    root = r"C:\g7core\g7_v1"
    docs = [
        "STATE_PACK\\DELTA_PACK_최신.txt", "라이트엔진.txt", "0110개발일지.txt", 
        "시스템구조베이직엔진.txt", "vmcl최종개념.txt", "네비게이터부분테슬라.txt"
    ]
    tags = ["basic", "light", "fun", "navigator", "vmcl"]
    keywords = ["TODO", "미진", "구멍", "막힘", "용접", "통합", "구현", "연결"]
    
    extracted = {t: [] for t in tags}
    for doc in docs:
        path = os.path.join(root, doc)
        if not os.path.exists(path): continue
        tag_hint = "light" if "라이트" in doc else "vmcl" if "vmcl" in doc else "navigator" if "네비" in doc else "basic"
        
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if any(kw in line for kw in keywords) and len(line.strip()) > 10:
                    mid = f"WORK_V3_{len(extracted[tag_hint]) + 100}"
                    extracted[tag_hint].append({
                        "mission_id": mid,
                        "title": f"[{tag_hint.upper()}] {line.strip()[:30]}",
                        "objective": line.strip(),
                        "handler_type": "LLM",
                        "expected_outputs": [f"receipts\\mission\\res_{mid}.json"],
                        "acceptance": "main\\manager.py 등록/호출 흔적 포함 필수"
                    })

    # 600발 쿼터 배분 (각 태그 120개 타겟)
    final_missions = []
    for t in tags:
        pool = extracted[t]
        while len(pool) < 120: # 부족분 채우기
            pool.append({"mission_id": f"FILL_{t}_{len(pool)}", "title": f"Refine {t} module", "objective": f"Optimize {t} logic", "handler_type": "LLM", "expected_outputs": [f"receipts\\mission\\res_FILL_{t}.json"], "acceptance": "manager.py check"})
        final_missions.extend(pool[:120])

    # 파일 생성
    cat_path = os.path.join(root, "engine", "mission_catalog_work_v3.json")
    with open(cat_path, 'w', encoding='utf-8') as f: json.dump(final_missions, f, indent=2)
    
    # 오더 및 큐 생성
    queue_list = []
    for i, label in enumerate(['C', 'D', 'E', 'F', 'G']):
        fname = f"REAL_WORK_120_{label}.txt"
        fpath = os.path.join(root, "GPTORDER", fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            for m in final_missions[i*120:(i+1)*120]: f.write(f"{m['mission_id']}\n")
        queue_list.append(fpath)
    
    q_path = os.path.join(root, "GPTORDER", "NIGHT_QUEUE_WORK_600.txt")
    with open(q_path, 'w', encoding='utf-8') as f:
        for q in queue_list: f.write(q + "\n")
        
    print(f">>> [V3] Catalog & Queue Generated. Tags: { {t:120 for t in tags} }")

if __name__ == "__main__": build_v3()