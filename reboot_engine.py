import os, json, csv, hashlib, sys

def run(run_dir):
    chunk_dir = r"C:\g6core\g6_v24\data\umr\chunks"
    target_recs = []
    seen_sha1 = set()
    
    # [W001-W002] 재귀 스캔 및 120개 고유 레코드 추출
    for root, _, files in os.walk(chunk_dir):
        for f in files:
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f_in:
                    # JSONL이면 줄 단위, 아니면 통째로
                    lines = f_in if path.endswith('.jsonl') else [f_in.read()]
                    for line in lines:
                        clean_text = line.strip()
                        if len(clean_text) > 100:
                            h = hashlib.sha1(clean_text.encode()).hexdigest()
                            if h not in seen_sha1:
                                seen_sha1.add(h)
                                target_recs.append({"sha1": h, "text": clean_text, "source": os.path.basename(path)})
                        if len(target_recs) >= 120: break
            except: continue
            if len(target_recs) >= 120: break
    
    if len(target_recs) < 120:
        print(f"FATAL: Only {len(target_recs)} unique records found. Need 120."); sys.exit(1)

    # [W111] TRACK B 재료팩 생성
    with open(os.path.join(run_dir, "matrix_r1.csv"), "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["sha1", "source", "text"])
        writer.writeheader()
        writer.writerows(target_recs)
        
    with open(os.path.join(run_dir, "trackB_cases.jsonl"), "w", encoding="utf-8") as f:
        for i, r in enumerate(target_recs):
            case = {"case_id": i, "sha1": r['sha1'], "text": r['text'][:1000]}
            f.write(json.dumps(case, ensure_ascii=False) + "\n")
            
    print(f"REBOOT_DONE: 120 RECORDS SECURED AT {run_dir}")

if __name__ == "__main__":
    run(sys.argv[1])
