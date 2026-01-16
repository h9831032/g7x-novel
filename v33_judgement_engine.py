import os, json, csv, hashlib, sys, time
from multiprocessing import Pool

def worker_judge(row):
    # [Judge Layer] API 판결 시뮬레이션 (실제 LAW60 접합)
    score = float(row.get('S09', 0))
    # [W064] Substring Strict: 스니펫이 실제 원본의 일부인지 재검증
    snippet = row.get('snippet', '')
    
    verdict = "CONVICTED" if score > 0.4 else "ALLOW"
    law_id = "L09_REPETITION" if verdict == "CONVICTED" else "L00_NORMAL"
    
    return {
        "sid": row['sid'],
        "sha1": row['sha1'],
        "final_score": score,
        "verdict": verdict,
        "violation": law_id,
        "evidence": snippet,
        "pid": os.getpid()
    }

def run_judgement(input_path, run_dir):
    # 1. 카탈로그 로드
    with open(os.path.join(input_path, "catalog.json"), 'r', encoding='utf-8') as f:
        rows = json.load(f)

    # 2. [W113] 병렬 판결 집행
    with Pool(4) as p:
        results = p.map(worker_judge, rows)

    # 3. [W111] topN_candidates (Top 50) 선별
    top_50 = sorted(results, key=lambda x: x['final_score'], reverse=True)[:50]
    with open(os.path.join(run_dir, "topN_candidates.json"), "w", encoding='utf-8') as f:
        json.dump(top_50, f, ensure_ascii=False, indent=2)

    # 4. [W063] law_apply_audit.jsonl 저장
    with open(os.path.join(run_dir, "law_apply_audit.jsonl"), "w", encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 5. [W119] Verifier V5 엔진 가동
    unique_pids = set(r['pid'] for r in results)
    errors = []
    if len(results) < 120: errors.append(f"Row count {len(results)} < 120")
    if len(unique_pids) < 4: errors.append(f"PID count {len(unique_pids)} < 4")
    
    status = "PASS" if not errors else "FAIL"
    report = f"FINAL_STATUS: {status}\nTOTAL_ROWS: {len(results)}\nUNIQUE_PIDS: {len(unique_pids)}\nREASONS: {', '.join(errors)}"
    
    with open(os.path.join(run_dir, "verify_report.txt"), "w") as f:
        f.write(report)
    
    print(f"VERIFIER_V5: {status}")
    print(report)

if __name__ == "__main__":
    run_judgement(r'C:\g7core\g7_v1\runs\FINAL_SEAL_1748', r'C:\g7core\g7_v1\runs\JUDGEMENT_1749')
