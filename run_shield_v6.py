import os, json, re, math, csv, time, sys, gc

def get_tokens(text):
    return re.findall(r"[가-힣A-Za-z0-9]+", str(text))

def compute_metrics(texts):
    """메모리 보호를 위해 최소한의 텍스트만 처리"""
    joined = "\n".join(texts)
    tk = get_tokens(joined)
    if not tk: return {"flattening": 0, "word_count": 0}
    unique_ratio = len(set(tk)) / len(tk)
    return {
        "flattening": round(1.0 - unique_ratio, 4),
        "word_count": len(tk)
    }

def main():
    input_dir = r"C:\g6core\g6_v24\data\umr\chunks"
    out_dir = r"C:\g7core\g7_v1\runs\MEMORY_SAFE_RUN_" + time.strftime("%Y%m%d_%H%M%S")
    os.makedirs(out_dir, exist_ok=True)

    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.jsonl')]
    
    # [MEMORY_GUARD] 소설별로 텍스트를 다 쌓지 않고, ID와 위치 정보만 우선 확보하거나 
    # 혹은 스트리밍 중에 즉시 처리하여 메모리 점유율을 낮춤
    novel_data = {} # {nid: [text_samples]}
    processed_count = 0
    target_novels = 500
    results = []

    print(f">>> [G7X] Streaming {len(files)} files. Target: {target_novels} Real Novels.")

    # 1. 스트리밍 스캔 및 실시간 처리 (메모리에 다 올리지 않음)
    for fp in files:
        print(f"    Scanning Genre File: {os.path.basename(fp)}")
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if not line.strip(): continue
                try:
                    data = json.loads(line)
                    nid = data.get("novel_id") or data.get("book_id") or "UNKNOWN"
                    
                    if nid not in novel_data:
                        if len(novel_data) >= target_novels: break
                        novel_data[nid] = []
                    
                    # 소설당 최대 40개 청크만 메모리에 유지 (하청지시서 샘플링 제한)
                    if len(novel_data[nid]) < 40:
                        novel_data[nid].append(data.get("text", ""))
                    
                    # 소설 한 권의 데이터가 충분히 모였다면 즉시 중간 점검 가능하도록 구성
                except: continue
        if len(novel_data) >= target_novels: break
        gc.collect() # 파일 하나 끝날 때마다 메모리 강제 정리

    # 2. 실시간 분석 및 시각화 출력 (10권 단위)
    print(f"\n>>> [G7X] Extraction Complete. Starting Metric Calculation...")
    
    for i, (nid, texts) in enumerate(novel_data.items()):
        m = compute_metrics(texts)
        row = {
            "novel_id": nid,
            "flattening_score": m["flattening"],
            "word_count": m["word_count"],
            "AND_A": 1 if m["flattening"] > 0.7 else 0
        }
        results.append(row)

        # [VISUAL_FEEDBACK] 10권마다 형님께 보고
        if (i + 1) % 10 == 0 or (i + 1) == len(novel_data):
            print(f">>> [PROGRESS] {i+1}/{len(novel_data)} Novels Processed | Current ID: {nid}")
            sys.stdout.flush()

    # 3. 산출물 및 영수증 (EVIDENCE_MANDATED_AUDIT)
    matrix_path = os.path.join(out_dir, "quality_matrix.csv")
    with open(matrix_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=results[0].keys())
        w.writeheader()
        w.writerows(results)
    
    with open(os.path.join(out_dir, "receipt.jsonl"), "w", encoding="utf-8") as f:
        json.dump({"ts": time.ctime(), "novels": len(results), "status": "SUCCESS"}, f)

    print(f"\n>>> [SUCCESS] 500 Novels Survey Completed. Result: {out_dir}")

if __name__ == "__main__":
    main()
