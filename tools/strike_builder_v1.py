import sys, json, os

def build_strike(run_dir):
    idx_path = os.path.join(run_dir, "library_index.jsonl")
    tag_path = os.path.join(run_dir, "tag_index_rules.jsonl")
    out_path = os.path.join(run_dir, "strike_list.jsonl")
    
    tags = {}
    with open(tag_path, "r", encoding="utf-8") as f_tag:
        for line in f_tag:
            d = json.loads(line)
            tags[d["chunk_id"]] = d["tags"]
            
    strike_count = 0
    with open(idx_path, "r", encoding="utf-8") as f_idx, open(out_path, "w", encoding="utf-8") as f_out:
        for line in f_idx:
            idx = json.loads(line)
            tag = tags.get(idx["chunk_id"], {})
            
            if tag.get("needs_strike"):
                strike_rec = {
                    "chunk_id": idx["chunk_id"],
                    "file_path": idx["file_path"],
                    "offset": idx["offset"],
                    "length": idx["length"],
                    "reasons": tag["reasons"],
                    "risk": tag["risk"]
                }
                f_out.write(json.dumps(strike_rec, ensure_ascii=False) + "\n")
                strike_count += 1
    return strike_count

if __name__ == "__main__":
    cnt = build_strike(sys.argv[1])
    print(cnt)