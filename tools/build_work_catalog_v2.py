import json
import os
import re
from datetime import datetime

def build_v2_1():
    root = r"C:\g7core\g7_v1"
    target_count = 600
    quotas = {"basic": 180, "light": 150, "fun": 90, "navigator": 90, "vmcl": 90}
    
    # A2. 스캔 대상 명시적 리스트
    scan_files = [
        "라이트엔진.txt", "반자동ai생산시스템.txt", "시스템구조베이직엔진.txt",
        "vmcl최종개념.txt", "네비게이터부분테슬라.txt", "오류시스템정리12.28.txt",
        "STATE_PACK\\DEVLOG_20260111.txt"
    ]
    
    # A1. 파일명 기반 태그 매핑 로직
    def get_tag_by_filename(fname):
        fname = fname.lower()
        if "라이트" in fname or "light" in fname: return "light"
        if "네비" in fname or "navigator" in fname: return "navigator"
        if "vmcl" in fname: return "vmcl"
        if "fun" in fname or "재미" in fname: return "fun"
        return "basic"

    extracted_tasks = {k: [] for k in quotas.keys()}
    file_stats = {}

    # A3. TODO 추출량 증대 (키워드 보강)
    keywords = ["통합", "용접", "플러그인", "등록", "호출", "메인", "연결", "리콜", "포인터", "센서", "재미"]
    
    for rel_path in scan_files:
        abs_path = os.path.join(root, rel_path)
        if not os.path.exists(abs_path): continue
        
        tag = get_tag_by_filename(rel_path)
        with open(abs_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            count = 0
            for line in lines:
                line = line.strip()
                if len(line) > 10 and any(kw in line for kw in keywords):
                    mid = f"W_{tag.upper()}_{len(extracted_tasks[tag]) + 100}"
                    extracted_tasks[tag].append({
                        "mission_id": mid,
                        "title": f"[{tag.upper()}] {line[:20]}",
                        "handler_type": "LLM",
                        "objective": line,
                        "expected_outputs": [f"receipts\\mission\\res_{mid}.json"],
                        "acceptance": "file_exists"
                    })
                    count += 1
            file_stats[rel_path] = count

    # A4. 태그 쿼터 강제 배분 및 Filler 채우기
    final_catalog = []
    for tag, limit in quotas.items():
        tasks = extracted_tasks[tag][:limit]
        # 부족분 Filler 생성
        while len(tasks) < limit:
            idx = len(tasks)
            mid = f"F_{tag.upper()}_{idx}"
            tasks.append({
                "mission_id": mid, "title": f"Filler {tag} {idx}",
                "handler_type": "LOCAL", "objective": f"Sync {tag} module",
                "expected_outputs": [f"receipts\\mission\\res_{mid}.json"],
                "acceptance": "file_exists"
            })
        final_catalog.extend(tasks)

    # A5. 결과 검증 REPORT 생성
    report = {
        "BACKLOG_COUNT": sum(file_stats.values()),
        "TAG_COUNT": {tag: len([t for t in final_catalog if tag.lower() in t['mission_id'].lower() or tag.lower() in t['title'].lower()]) for tag in quotas},
        "FILE_STATS": file_stats,
        "SAMPLES": {tag: [t['mission_id'] for t in extracted_tasks[tag][:3]] for tag in quotas}
    }
    
    # 파일 쓰기
    cat_path = os.path.join(root, "engine", "mission_catalog_work_v2.json")
    rep_path = os.path.join(root, "engine", f"work_catalog_v2_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    with open(cat_path, 'w', encoding='utf-8') as f: json.dump(final_catalog, f, indent=2)
    with open(rep_path, 'w', encoding='utf-8') as f: json.dump(report, f, indent=2)
    
    print(f">>> [V2.1] Catalog & Report Generated. Total: {len(final_catalog)}")
    return rep_path

if __name__ == "__main__":
    build_v2_1()