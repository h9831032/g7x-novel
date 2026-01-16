import os, json, csv, hashlib, sys, time

def sha1(t): return hashlib.sha1(t.encode()).hexdigest()

def run_stream(rot_id, run_dir):
    chunk_dir = r"C:\g6core\g6_v24\data\umr\chunks"
    target_recs = []
    
    print(f"\n>>> [ROTATION {rot_id}] MINE START...")
    sys.stdout.flush()

    # [FIX] os.listdir 대신 scandir 사용하여 속도 및 메모리 효율 극대화
    count = 0
    with os.scandir(chunk_dir) as it:
        for entry in it:
            if entry.name.endswith('.jsonl') and entry.is_file():
                try:
                    with open(entry.path, 'r', encoding='utf-8', errors='ignore') as f:
                        # 120개 채굴 시 실시간 로그
                        text = f.read(1500)
                        if len(text) > 100:
                            h = sha1(text)
                            target_recs.append({"sid": f"R{rot_id}_{count}", "sha1": h, "text": text})
                            print(f"[STREAM] {rot_id}-{count:03d}: {h[:12]} SECURED", end='\r')
                            sys.stdout.flush()
                            count += 1
                except: continue
            if count >= 120: break

    # [3단 레이어 실전 주행]
    results = []
    for r in target_recs:
        words = r['text'].split()
        s09 = round(1.0 - (len(set(words))/len(words)), 4) if words else 0
        results.append({
            "sid": r['sid'], "sha1": r['sha1'], "S09": s09, 
            "law": "L09_REP" if s09 > 0.4 else "L00_OK"
        })

    # 영수증 즉시 저장
    matrix_p = os.path.join(run_dir, f"matrix_rot_{rot_id}.csv")
    with open(matrix_p, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n>>> [ROTATION {rot_id}] DONE: 120 RECORDS SEALED.")
    sys.stdout.flush()

if __name__ == "__main__":
    for rot in ['A', 'B', 'C']:
        r_path = os.path.join(r'C:\g7core\g7_v1\runs\V29_FIX_1757', f"ROT_{rot}")
        os.makedirs(r_path, exist_ok=True)
        run_stream(rot, r_path)
