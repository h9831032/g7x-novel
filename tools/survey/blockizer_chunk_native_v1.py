import os
import json

def build_chunk_native_sbl(chunks, wid):
    l0_blocks = []
    for i, body in enumerate(chunks):
        # [도시락] 앞 정크 끝 300자 + 본문 + 뒤 정크 앞 300자
        prev_tail = chunks[i-1][-300:] if i > 0 else ""
        next_head = chunks[i+1][:300] if i < len(chunks)-1 else ""
        
        l0_blocks.append({
            "wid": wid, "level": "L0", "idx": i,
            "prev_tail": prev_tail, "body": body, "next_head": next_head
        })
    
    # L1: 3개 묶음 (stride 1) / L2: 10개 묶음 (stride 3)
    l1 = [{"level":"L1", "idx": i, "body":"".join(chunks[i:i+3])} for i in range(len(chunks)-2)]
    l2 = [{"level":"L2", "idx": i, "body":"".join(chunks[i:i+10])} for i in range(0, len(chunks)-9, 3)]
    return l0_blocks, l1, l2
