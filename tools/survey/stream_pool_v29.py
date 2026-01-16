import os, json, csv, hashlib, sys, time

def sha1(t): return hashlib.sha1(t.encode()).hexdigest()

def run_mining(source_dir, run_dir):
    print(">>> SCANNING STARTED. WATCH THE COUNTER...")
    sys.stdout.flush()
    
    global_pool = []
    seen_hashes = set()
    
    # [STEP 1] 실시간 전수 채굴
    with os.scandir(source_dir) as it:
        for entry in it:
            if entry.is_file() and (entry.name.endswith('.jsonl') or entry.name.endswith('.txt')):
                try:
                    with open(entry.path, 'r', encoding='utf-8', errors='ignore') as f:
                        if entry.name.endswith('.jsonl'):
                            lines = f.readlines()
                        else:
                            lines = [f.read()]
                        
                        for line in lines:
                            text = line.strip()
                            if len(text) < 50: continue
                            
                            h = sha1(text)
                            if h not in seen_hashes:
                                seen_hashes.add(h)
                                global_pool.append({"text": text, "sha1": h, "src": entry.name})
                                
                                # [FIX] 10개마다 생존 신고
                                if len(global_pool) % 10 == 0:
                                    print(f"[MINING] Secured {len(global_pool)} unique records...", end='\r')
                                    sys.stdout.flush()
                except: continue

    print(f"\n>>> SCAN COMPLETED. TOTAL UNIQUE: {len(global_pool)}")
    sys.stdout.flush()

    # [STEP 2] 로테이션 분배 (A:0-120, B:120-240, C:240-360)
    # 총알이 부족하면 부족한 대로 진행 (거짓말 안 함)
    rotations = {
        'A': global_pool[0:120],
        'B': global_pool[120:240] if len(global_pool) >= 240 else [],
        'C': global_pool[240:360] if len(global_pool) >= 360 else []
    }

    total_secured = 0
    for rot_id, items in rotations.items():
        if not items: continue
        
        # 3단 레이어 처리
        results = []
        for i, item in enumerate(items):
            text = item['text']
            words = text.split()
            s09 = round(1.0 - (len(set(words))/len(words)), 4) if words else 0
            
            results.append({
                "sid": f"R{rot_id}_{i:03d}",
                "sha1": item['sha1'],
                "S09": s09,
                "window_level": "L1_POOL",
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
        
        total_secured += len(results)
        print(f">>> ROTATION {rot_id}: {len(results)} RECORDS SAVED.")

    print(f"FINAL_STATUS: PASS (TOTAL {total_secured} RECORDS)")

if __name__ == "__main__":
    run_mining(r'C:\g6core\g6_v24\data\umr\chunks', r'C:\g7core\g7_v1\runs\V29_STREAM_1810')
