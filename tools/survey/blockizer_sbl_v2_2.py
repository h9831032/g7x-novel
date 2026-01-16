import re
import os

def adaptive_cut(text, target=1500, min_len=1000, max_len=2000):
    if len(text) <= max_len: return len(text)
    search_zone = text[min_len:max_len]
    for pattern in [r'\n\n', r'["'']\n', r'\.\s', r'\.']:
        matches = list(re.finditer(pattern, search_zone))
        if matches: return min_len + matches[-1].end()
    return target

def build_sbl_v2_2(text, wid):
    blocks = []
    start, overlap = 0, 200
    while start < len(text):
        chunk = text[start:]
        cut = adaptive_cut(chunk)
        body = chunk[:cut]
        # [도시락 반찬] 앞뒤 300자 결착 
        blocks.append({
            "wid": wid, "level": "L0",
            "prev_tail": text[max(0, start-300):start],
            "body": body,
            "next_head": text[start+cut:start+cut+300]
        })
        if start + cut >= len(text): break
        start += (cut - overlap)
    return blocks
