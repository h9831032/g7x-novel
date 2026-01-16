import re

def adaptive_cut(text, target=1500, min_len=1000, max_len=2000):
    if len(text) <= max_len: return len(text)
    search_zone = text[min_len:max_len]
    for pattern in [r'\n\n', r'\.\s', r'\.']:
        matches = list(re.finditer(pattern, search_zone))
        if matches: return min_len + matches[-1].end()
    return target

def build_sbl_v2_1(text, wid):
    l0 = []
    start, overlap = 0, 200
    while start < len(text):
        chunk = text[start:]
        cut = adaptive_cut(chunk)
        body = chunk[:cut]
        l0.append({
            "wid": wid, "level": "L0",
            "prev_tail": text[max(0, start-300):start],
            "body": body,
            "next_head": text[start+cut:start+cut+300]
        })
        if start + cut >= len(text): break
        start += (cut - overlap)
    
    l1 = [{"level":"L1", "body":"".join([b['body'] for b in l0[i:i+3]])} for i in range(0, len(l0)-2, 2)]
    l2 = [{"level":"L2", "body":"".join([b['body'] for b in l0[i:i+10]])} for i in range(0, len(l0)-9, 6)]
    return l0, l1, l2
