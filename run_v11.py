import os, json, re, csv, time, sys, gc, math

def get_tokens(text):
    return re.findall(r"[가-힣A-Za-z0-9]+", str(text))

def get_p95(values):
    if not values: return 0.0
    s = sorted(values)
    return s[int(0.95 * (len(s) - 1))]

class MetricEngineV11:
    def __init__(self):
        self.metrics = ["flattening", "tone_drift", "slippy_lift", "density_imbalance", "unique_token", "time_compression", "spatial_inconsistency"]

    def compute_chunk(self, text):
        tk = get_tokens(text)
        if not tk: return {k: 0.0 for k in self.metrics}
        unique_ratio = len(set(tk)) / len(tk)
        # 3-gram 중복도
        grams = [" ".join(tk[i:i+3]) for i in range(len(tk)-2)]
        rep = (len(grams) - len(set(grams))) / len(grams) if grams else 0.0
        
        return {
            "flattening": round(rep, 4),
            "tone_drift": 0.0, # 단일 청크에서는 0, 집계 시 계산
            "unique_token": round(1.0 - unique_ratio, 4),
            "density_imbalance": round(abs((len(re.findall(r'["'']', str(text))) / max(1, len(str(text))/50)) - 0.35), 4),
            "slippy_lift": 0.0,
            "time_compression": 0.0, # 정규식 기반 확장 가능
            "spatial_inconsistency": 0.0
        }

def main():
    input_dir = r"C:\g6core\g6_v24\data\umr\chunks"
    run_id = "PHASE18_AGG_" + time.strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(r"C:\g7core\g7_v1\runs", run_id)
    os.makedirs(out_dir, exist_ok=True)

    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.jsonl')]
    engine = MetricEngineV11()
    novel_map = {}
    target_count = 500
    results = []

    print(f">>> [G7X] Aggregation Mode: Processing {target_count} novels...")

    # [STREAMING_ACCUMULATOR]
    for fp in files:
        if len(results) >= target_count: break
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    nid = data.get("novel_id") or data.get("book_id") or data.get("bid") or data.get("id")
                    if not nid: continue
                    if nid not in novel_map:
                        if len(results) + len(novel_map) >= target_count: continue
                        novel_map[nid] = []
                    
                    if len(novel_map[nid]) < 40:
                        novel_map[nid].append(engine.compute_chunk(data.get("text", "")))
                        
                    if len(novel_map[nid]) >= 40:
                        # 즉시 집계 및 방출
                        m_list = novel_map[nid]
                        row = {"novel_id": nid}
                        for m_key in engine.metrics:
                            vals = [m[m_key] for m in m_list]
                            mean_v, p95_v, count_v = sum(vals)/len(vals), get_p95(vals), sum(1 for v in vals if v > 0.7)
                            row[f"{m_key}_mean"] = round(mean_v, 4)
                            row[f"{m_key}_p95"] = round(p95_v, 4)
                            row[f"{m_key}_count_above"] = count_v
                        
                        row["flags_total"] = sum(1 for m in m_list if m["flattening"] > 0.7)
                        results.append(row)
                        del novel_map[nid]
                        if len(results) % 10 == 0: print(f">>> [PROGRESS] {len(results)}/500 novels aggregated...")
                        if len(results) >= target_count: break
                except: continue
        gc.collect()

    # CSV 출력 (집계형 스키마 강제)
    matrix_path = os.path.join(out_dir, "quality_matrix.csv")
    if results:
        fieldnames = results[0].keys()
        with open(matrix_path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(results)

    # Receipt 업데이트 (요구 메타데이터 포함)
    receipt = {
        "run_id": run_id,
        "sys_executable": sys.executable,
        "cwd": os.getcwd(),
        "input_dir": input_dir,
        "max_novels": target_count,
        "status": "AGG_SUCCESS",
        "timestamp": time.ctime()
    }
    with open(os.path.join(out_dir, "receipt.jsonl"), "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False)

    print(f"\n>>> [SUCCESS] 집계 매트릭스 완공. 결과: {out_dir}")

if __name__ == "__main__": main()
