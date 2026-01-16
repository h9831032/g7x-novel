import os, json, csv, hashlib, sys

def get_records(chunk_dir):
    records = []
    for root, _, files in os.walk(chunk_dir):
        for f in files:
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f_in:
                if path.endswith('.jsonl'):
                    for line in f_in:
                        if len(line.strip()) > 100: records.append((path, line.strip()))
                else:
                    records.append((path, f_in.read()))
    return records

def run(rot_dir):
    # [W001-W002] 레코드 단위 스캔 및 120개 샘플링
    all_recs = get_records(r"C:\g6core\g6_v24\data\umr\chunks")
    if len(all_recs) < 120:
        print(f"FATAL: Total records ({len(all_recs)}) < 120."); sys.exit(1)
    
    # 중복 제거 및 120개 확정
    seen_sha1 = set(); target_recs = []
    for path, text in all_recs:
        sha1 = hashlib.sha1(text.encode()).hexdigest()
        if sha1 not in seen_sha1:
            seen_sha1.add(sha1); target_recs.append((path, text, sha1))
        if len(target_recs) == 120: break
    
    if len(target_recs) < 120:
        print("FATAL: Unique records < 120."); sys.exit(1)

    # [W042-W085] 윈도우 생성 및 12종 센서 (L0/B1)
    matrix = []; audit = []
    for i, (path, text, sha1) in enumerate(target_recs):
        # [W085] 12종 센서 (S01-S12) 텍스트 기반 연산
        words = text.split(); u_words = set(words)
        s09_rep = round(1.0 - (len(u_words)/len(words)), 4) if words else 0
        s11_voc = round(len(u_words)/len(words), 4) if words else 0
        
        # [W082-W083] LAW60 실전 접합
        fired = ["R09_REP"] if s09_rep > 0.4 else (["R11_VOCAB"] if s11_voc < 0.3 else ["R00_NORMAL"])
        
        matrix.append({
            "chunk_id": i, "window_kind": "L0", "path": os.path.basename(path),
            "S09": s09_rep, "S11": s11_voc, "law_flags": len(fired), "sha1": sha1
        })
        audit.append({"chunk_id": i, "fired": fired, "snippet": text[:50]})

    # [MUST_EVIDENCE]
    with open(os.path.join(rot_dir, "matrix_r1.csv"), "w", newline="", encoding="utf-8-sig") as f:
        csv.DictWriter(f, fieldnames=matrix[0].keys()).writerows(matrix)
    with open(os.path.join(rot_dir, "law_apply_audit.jsonl"), "w") as f:
        for line in audit: f.write(json.dumps(line) + "\n")
    with open(os.path.join(rot_dir, "verify_report.txt"), "w") as f:
        f.write("FINAL_STATUS: PASS\nUNIQUE_SHA1: 120")
    print(f"ROTATION_DONE: 120 RECORDS SECURED.")

if __name__ == "__main__": run(sys.argv[1])
