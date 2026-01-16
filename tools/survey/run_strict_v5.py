import os, json, csv, hashlib, sys

def run(run_dir):
    input_dir = r"C:\g6core\g6_v24\data\umr\chunks"
    # [W095] 120개 강제 타격 (파일이 없으면 FAIL)
    all_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(('.jsonl', '.json', '.txt'))]
    if len(all_files) < 120:
        print(f"CRITICAL: Found only {len(all_files)} chunks. 120-ROWS FAIL."); sys.exit(1)
    
    target_files = all_files[:120]
    matrix = []
    
    for i, p in enumerate(target_files):
        with open(p, 'r', encoding='utf-8', errors='ignore') as f: text = f.read(2000)
        
        # [W043] 텍스트 기반 결정론적 센서 (고정값 금지)
        words = text.split(); u_words = set(words)
        s09 = round(1.0 - (len(u_words)/len(words)), 4) if words else 0
        s11 = round(len(u_words)/len(words), 4) if words else 0
        
        # [W044] LAW60 (가변 발동)
        fired = ["R09_REPEAT"] if s09 > 0.4 else (["R11_LOW_VOCAB"] if s11 < 0.3 else ["R00_NORMAL"])
        
        matrix.append({
            "chunk_id": i, "kind": "L0", "path": os.path.basename(p),
            "S09": s09, "S11": s11, "law_flags": len(fired), "fired_list": "|".join(fired),
            "sha1": hashlib.sha1(text.encode()).hexdigest()
        })
    
    # [MUST_EVIDENCE]
    with open(os.path.join(run_dir, "matrix_r1.csv"), "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=matrix[0].keys()); writer.writeheader(); writer.writerows(matrix)
    
    # [W091] Verifier V5 Strict Check
    unique_sha1 = len(set(m['sha1'] for m in matrix))
    status = "PASS" if (len(matrix) == 120 and unique_sha1 >= 100) else "FAIL"
    
    with open(os.path.join(run_dir, "receipt.json"), "w") as f:
        json.dump({"rows": len(matrix), "unique_sha1": unique_sha1, "status": status}, f, indent=2)
    
    with open(os.path.join(run_dir, "verify_report.txt"), "w") as f:
        f.write(f"FINAL_STATUS: {status}\nREASON: SHA1_UNIQUE={unique_sha1}, ROWS={len(matrix)}")
    
    print(f"STRICT_DONE: {len(matrix)} rows processed. Status: {status}")

if __name__ == "__main__": run(sys.argv[1])
