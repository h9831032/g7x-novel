import sys, json, os

def run_tagging(run_dir):
    idx_p, tag_p, str_p = os.path.join(run_dir, "library_index.jsonl"), os.path.join(run_dir, "tag_index_rules.jsonl"), os.path.join(run_dir, "strike_list.jsonl")
    danger = ["오류", "붕괴", "모순", "급변", "이상함", "반복", "석화"]
    s_cnt = 0
    with open(idx_p, "r", encoding="utf-8") as f_in, open(tag_p, "w", encoding="utf-8") as f_t, open(str_p, "w", encoding="utf-8") as f_s:
        for line in f_in:
            idx = json.loads(line)
            if "skip_reason" in idx: continue
            reasons = [w for w in danger if w in idx["text_preview"]]
            hit = len(reasons) > 0
            t_rec = {"chunk_id": idx["chunk_id"], "tags": {"needs_strike": hit, "reasons": reasons}}
            f_t.write(json.dumps(t_rec, ensure_ascii=False) + "\n")
            if hit:
                idx.update({"reasons": reasons})
                f_s.write(json.dumps(idx, ensure_ascii=False) + "\n"); s_cnt += 1
    return s_cnt

if __name__ == "__main__":
    print(run_tagging(sys.argv[1]))