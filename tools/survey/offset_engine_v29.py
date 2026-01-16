import os, json, csv, hashlib, sys

def sha1(t): return hashlib.sha1(t.encode()).hexdigest()

def run_rotation(rot_id, run_dir, file_list):
    # [W015] 로테이션별 오프셋 슬라이싱 (A:0, B:120, C:240)
    offset_map = {'A': 0, 'B': 120, 'C': 240}
    start_idx = offset_map[rot_id]
    target_files = file_list[start_idx : start_idx + 120]
    
    if len(target_files) < 120:
        print(f"FATAL: Not enough files for Rotation {rot_id}"); sys.exit(1)

    results = []
    for i, entry in enumerate(target_files):
        with open(entry.path, 'r', encoding='utf-8', errors='ignore') as f:
            # [W002] L1(B1) 윈도우 시뮬레이션: 3개 유닛 결합 시도
            text = f.read(2000) 
            h = sha1(text)
            
            # Cheap Layer (S09)
            words = text.split()
            s09 = round(1.0 - (len(set(words))/len(words)), 4) if words else 0
            
            results.append({
                "sid": f"S_{rot_id}_{i:03d}",
                "sha1": h,
                "S09": s09,
                "window_level": "L1",
                "window_kind": "CHUNK_NATIVE",
                "source_file": entry.name
            })

    # [W120] 영수증 봉인
    matrix_p = os.path.join(run_dir, f"matrix_r1_{rot_id}.csv")
    with open(matrix_p, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"ROTATION_{rot_id}_DONE: {len(results)} UNIQUE RECORDS (START_OFFSET: {start_idx})")
    return [r['sha1'] for r in results]

if __name__ == "__main__":
    # 전체 파일 리스트를 먼저 결정론적으로 정렬 (재현성 확보)
    all_entries = sorted([e for e in os.scandir(r'C:\g6core\g6_v24\data\umr\chunks') if e.is_file() and e.name.endswith('.jsonl')], key=lambda x: x.name)
    
    global_hashes = []
    for rot in ['A', 'B', 'C']:
        r_path = os.path.join(r'C:\g7core\g7_v1\runs\V29_FINAL_1805', f"ROT_{rot}")
        os.makedirs(r_path, exist_ok=True)
        new_hashes = run_rotation(rot, r_path, all_entries)
        
        # [W017, W018] 중복 체크
        overlap = set(global_hashes) & set(new_hashes)
        if overlap:
            print(f"FATAL: Duplicate hash detected between rotations! Count: {len(overlap)}"); sys.exit(1)
        global_hashes.extend(new_hashes)
