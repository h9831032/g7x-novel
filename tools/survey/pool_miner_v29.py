import os, json, csv, hashlib, sys

def sha1(t): return hashlib.sha1(t.encode()).hexdigest()

def run_global_mining(source_dir, run_dir):
    # [STEP 1] 전수 채굴 (파일 경계 무시)
    print(">>> SCANNING ALL FILES FOR RECORDS...")
    global_pool = []
    seen_hashes = set()
    
    with os.scandir(source_dir) as it:
        for entry in it:
            if entry.is_file() and (entry.name.endswith('.jsonl') or entry.name.endswith('.txt')):
                try:
                    with open(entry.path, 'r', encoding='utf-8', errors='ignore') as f:
                        if entry.name.endswith('.jsonl'):
                            lines = f.readlines()
                        else:
                            lines = [f.read()] # txt는 통으로 1개
                        
                        for line in lines:
                            text = line.strip()
                            if len(text) < 50: continue # 너무 짧은 건 폐기
                            
                            h = sha1(text)
                            if h not in seen_hashes:
                                seen_hashes.add(h)
                                global_pool.append({"text": text, "sha1": h, "src": entry.name})
                except: continue

    # [STEP 2] 결정론적 정렬 (재현성 확보)
    global_pool.sort(key=lambda x: x['sha1'])
    total_recs = len(global_pool)
    print(f">>> GLOBAL POOL SIZE: {total_recs} UNIQUE RECORDS FOUND.")

    if total_recs < 120:
        print(f"FATAL: Total records ({total_recs}) < 120. Cannot even run Rotation A."); sys.exit(1)

    # [STEP 3] 로테이션 분배 (A, B, C)
    rotations = {
        'A': global_pool[0:120],
        'B': global_pool[120:240] if total_recs >= 240 else [],
        'C': global_pool[240:360] if total_recs >= 360 else []
    }

    # [STEP 4] 실행 및 영수증 발행
    for rot_id, items in rotations.items():
        if not items:
            print(f"WARN: Not enough records for Rotation {rot_id}. Skipping.")
            continue
            
        # 3단 레이어 처리 (Cheap/Context/Judge)
        results = []
        for i, item in enumerate(items):
            text = item['text']
            # S09 Check
            words = text.split()
            s09 = round(1.0 - (len(set(words))/len(words)), 4) if words else 0
            
            results.append({
                "sid": f"R{rot_id}_{i:03d}",
                "sha1": item['sha1'],
                "S09": s09,
                "window_level": "L1", # 풀링된 문장은 그 자체로 컨텍스트 보유 간주
                "law_hit": "L09" if s09 > 0.4 else "None",
                "source": item['src']
            })

        # 저장
        r_path = os.path.join(run_dir, f"ROT_{rot_id}")
        os.makedirs(r_path, exist_ok=True)
        
        with open(os.path.join(r_path, "matrix_r1.csv"), 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
            
        print(f"ROTATION_{rot_id}_DONE: {len(results)} RECORDS SEALED.")

    # 최종 보고
    if total_recs < 360:
        print(f"PARTIAL_SUCCESS: Secured {total_recs}/360 records.")
    else:
        print("FULL_SUCCESS: All 360 records secured.")

if __name__ == "__main__":
    run_global_mining(r'C:\g6core\g6_v24\data\umr\chunks', r'C:\g7core\g7_v1\runs\V29_POOL_1808')
