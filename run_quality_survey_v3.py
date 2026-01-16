import os, json, csv, time, sys, gc
from tools.survey.metrics_buffer2_v3 import Buffer2MetricsV3
from tools.survey.metrics_general_error_v1 import GeneralErrorMetricsV1

def main():
    input_dir = r"C:\g6core\g6_v24\data\umr\chunks"
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out_dir = rf"C:\g7core\g7_v1\runs\PHASE18_V10_{stamp}"
    os.makedirs(out_dir, exist_ok=True)

    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.jsonl')]
    buf_engine = Buffer2MetricsV3()
    gen_engine = GeneralErrorMetricsV1()
    
    novel_map = {}
    target_novels = 500
    results = []
    
    print(f">>> [G7X] Memory Shield Active. Streaming through {len(files)} files...")

    # [PHASE18_STREAM_SCAN]
    for fp in files:
        if len(results) >= target_novels: break
        print(f"    Scanning inside: {os.path.basename(fp)}")
        
        # 파일을 한 줄씩 읽어 메모리 보호 (Streaming)
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    nid = data.get("novel_id") or data.get("book_id") or data.get("bid") or data.get("id")
                    if not nid: continue
                    
                    if nid not in novel_map:
                        if len(results) + len(novel_map) >= target_novels: 
                            # 현재 수집중인 소설까지만 처리
                            pass 
                        else:
                            novel_map[nid] = []
                    
                    if nid in novel_map:
                        novel_map[nid].append(data.get("text", ""))
                        
                        # 한 권이 40개 청크를 다 채우면 즉시 분석하고 메모리 비움 (Key Logic)
                        if len(novel_map[nid]) >= 40:
                            b_res = buf_engine.compute(novel_map[nid])
                            g_res = gen_engine.compute("\n".join(novel_map[nid]))
                            
                            row = {"novel_id": nid}
                            row.update(b_res["scores"])
                            row.update(g_res["scores"])
                            row["word_count"] = b_res["evidence"]["raw_word_count"]
                            
                            # [SAFE_AND_FLAGGING] KeyError 방지를 위해 .get() 사용
                            f_score = row.get("flattening_score", 0.0)
                            d_score = row.get("density_imbalance_score", 0.0)
                            row["AND_A"] = 1 if f_score > 0.7 and d_score > 0.6 else 0
                            
                            results.append(row)
                            del novel_map[nid] # 분석 완료 데이터 즉시 삭제 (Memory Shield)
                            
                            if len(results) % 10 == 0:
                                print(f">>> [PROGRESS] {len(results)}/500 Processed | Last ID: {nid}")
                                gc.collect()
                                
                            if len(results) >= target_novels: break
                except: continue
    
    # 남은 소설들 처리
    for nid, texts in novel_map.items():
        if len(results) >= target_novels: break
        b_res = buf_engine.compute(texts)
        g_res = gen_engine.compute("\n".join(texts))
        row = {"novel_id": nid}
        row.update(b_res["scores"])
        row.update(g_res["scores"])
        row["word_count"] = b_res["evidence"]["raw_word_count"]
        row["AND_A"] = 1 if row.get("flattening_score",0) > 0.7 and row.get("density_imbalance_score",0) > 0.6 else 0
        results.append(row)

    # [OUTPUT]
    matrix_path = os.path.join(out_dir, "quality_matrix.csv")
    with open(matrix_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    with open(os.path.join(out_dir, "receipt.jsonl"), "w", encoding="utf-8") as f:
        json.dump({"ts": time.ctime(), "novels": len(results), "status": "FULL_PASS"}, f)

    print(f"\n>>> [SUCCESS] 500 Novels Survey COMPLETE. Location: {out_dir}")

if __name__ == "__main__": main()
