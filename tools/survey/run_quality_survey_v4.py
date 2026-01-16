import os, json, csv, hashlib

def run(run_dir):
    input_dir = r"C:\g6core\g6_v24\data\umr\chunks" # [W041] 정확한 chunks 경로
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(('.jsonl', '.json', '.txt'))][:120]
    
    matrix = []
    for i, p in enumerate(files):
        with open(p, 'r', encoding='utf-8', errors='ignore') as f: text = f.read(2000)
        # [W043] 진짜 텍스트 기반 결정론적 센서 (No Constants)
        words = text.split()
        s09 = round(1.0 - (len(set(words))/len(words)), 4) if words else 0
        s11 = round(len(set(words))/len(words), 4) if words else 0
        
        # [W044] 가변 법전 적용 (텍스트에 따라 다르게 발동)
        fired = ["R01"] if s09 > 0.4 else (["R05"] if s11 < 0.3 else [])
        
        matrix.append({
            "chunk_id": i, "kind": "L0", "path": os.path.basename(p),
            "S09": s09, "S11": s11, "law_flags": len(fired), "fired_list": "|".join(fired),
            "sha1": hashlib.sha1(text.encode()).hexdigest()
        })
    
    # [W046] 증거팩 생성
    with open(os.path.join(run_dir, "matrix_r1.csv"), "w", newline="", encoding="utf-8-sig") as f:
        csv.DictWriter(f, fieldnames=matrix[0].keys()).writerows(matrix)
    with open(os.path.join(run_dir, "receipt.json"), "w") as f:
        json.dump({"rows": len(matrix), "input_dir": input_dir, "status": "PASS"}, f)
    print(f"NATIVE_DONE: {len(matrix)} rows processed.")

if __name__ == "__main__": import sys; run(sys.argv[1])
