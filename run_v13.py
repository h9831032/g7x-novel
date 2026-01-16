import os, json, re, csv, time, sys, gc

def get_tokens(text):
    return re.findall(r"[가-힣A-Za-z0-9]+", str(text))

def get_stats(values):
    if not values: return 0.0, 0.0, 0
    mean = sum(values) / len(values)
    sorted_v = sorted(values)
    p95 = sorted_v[int(0.95 * (len(sorted_v) - 1))]
    count_above = sum(1 for v in values if v > 0.7)
    return round(mean, 4), round(p95, 4), count_above

def main():
    input_dir = r"C:\g6core\g6_v24\data\umr\chunks"
    run_id = "PHASE18_AGG_V13_" + time.strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(r"C:\g7core\g7_v1\runs", run_id)
    os.makedirs(out_dir, exist_ok=True)

    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.jsonl')]
    target_count = 500
    novel_map = {} 
    results = []

    print(f">>> [G7X] Deep Scanning Inside Aggregated Files...")

    for fp in files:
        if len(results) >= target_count: break
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    nid = data.get("novel_id") or data.get("book_id") or data.get("id")
                    if not nid: continue
                    
                    if nid not in novel_map:
                        if len(results) + len(novel_map) >= target_count: continue
                        novel_map[nid] = []
                    
                    tk = get_tokens(data.get("text", ""))
                    if not tk: continue
                    unique_ratio = len(set(tk)) / len(tk)
                    novel_map[nid].append({"flat": 1.0 - unique_ratio, "len": len(tk)})
                    
                    # 40개 차면 즉시 처리 (메모리 보호)
                    if len(novel_map[nid]) >= 40:
                        m_list = novel_map.pop(nid)
                        f_vals = [m["flat"] for m in m_list]
                        mean_f, p95_f, cnt_f = get_stats(f_vals)
                        results.append({
                            "novel_id": nid,
                            "flattening_mean": mean_f, "flattening_p95": p95_f, "flattening_count_above": cnt_f,
                            "word_count_sum": sum(m["len"] for m in m_list), "flags_total": cnt_f
                        })
                        if len(results) % 10 == 0: print(f">>> [PROGRESS] {len(results)}/500 Collected...")
                        if len(results) >= target_count: break
                except: continue
        gc.collect()

    # [CRITICAL_FIX] 남은 소설들(40개 미만) 전수 처리 (Flushing)
    if len(results) < target_count:
        print(f">>> [G7X] Flushing remaining {len(novel_map)} novels...")
        for nid, m_list in list(novel_map.items()):
            if len(results) >= target_count: break
            f_vals = [m["flat"] for m in m_list]
            mean_f, p95_f, cnt_f = get_stats(f_vals)
            results.append({
                "novel_id": nid,
                "flattening_mean": mean_f, "flattening_p95": p95_f, "flattening_count_above": cnt_f,
                "word_count_sum": sum(m["len"] for m in m_list), "flags_total": cnt_f
            })
            del novel_map[nid]

    # 결과 물리적 쓰기
    matrix_path = os.path.join(out_dir, "quality_matrix.csv")
    if results:
        with open(matrix_path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=results[0].keys())
            w.writeheader()
            w.writerows(results)
            f.flush(); os.fsync(f.fileno())

    receipt = {
        "run_id": run_id, "novels": len(results), "input_dir": input_dir, 
        "max_novels": target_count, "sys_executable": sys.executable, "cwd": os.getcwd(), "status": "V13_AGG_SUCCESS"
    }
    with open(os.path.join(out_dir, "receipt.jsonl"), "w", encoding="utf-8") as f:
        json.dump(receipt, f)

    print(f"\n>>> [SUCCESS] V13 AGGREGATION COMPLETE: {out_dir}")

if __name__ == "__main__": main()
