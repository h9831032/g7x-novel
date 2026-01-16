import os, sys, json, hashlib, time, threading, re
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor

API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
MODEL_ID = "models/gemini-2.0-flash"

def get_res(client, p):
    prompt = "JSON only. {\"verdict\":\"ALLOW|BLOCK\",\"tags\":[]} \nPayload: " + p
    try:
        r = client.models.generate_content(model=MODEL_ID, contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0))
        return json.loads(r.text), hashlib.sha256(r.text.encode()).hexdigest(), True
    except: return {"verdict":"BLOCK","tags":[]}, "err", False

def process_batch(batch, run_dir):
    client = genai.Client(api_key=API_KEY)
    tag_p, str_p = os.path.join(run_dir, "tag_index_rules.jsonl"), os.path.join(run_dir, "strike_list.jsonl")
    s_cnt = 0
    with open(tag_p, "a", encoding="utf-8") as f_tag, open(str_p, "a", encoding="utf-8") as f_str:
        with ThreadPoolExecutor(max_workers=8) as ex:
            results = list(ex.map(lambda x: get_res(client, x['text_preview']), batch))
        for item, (res, h, ok) in zip(batch, results):
            tags = res.get("tags", [])
            hit = res.get("verdict") == "BLOCK" or len(tags) > 0
            t_rec = {"chunk_id": item["chunk_id"], "tags": tags, "v_h": h, "ok": ok}
            f_tag.write(json.dumps(t_rec, ensure_ascii=False) + "\n")
            if hit:
                item.update({"tags": tags, "v_h": h}); f_str.write(json.dumps(item, ensure_ascii=False) + "\n")
                s_cnt += 1
    return s_cnt

if __name__ == "__main__":
    run_dir = sys.argv[1]
    idx_p = os.path.join(run_dir, "library_index.jsonl")
    total_strike = 0
    batch = []
    with open(idx_p, "r", encoding="utf-8") as f:
        for line in f:
            batch.append(json.loads(line))
            if len(batch) >= 240:
                total_strike += process_batch(batch, run_dir)
                batch = []
        if batch: total_strike += process_batch(batch, run_dir)
    print(total_strike)