import os
import json
import sys
from pathlib import Path

def create_blocks(text, novel_id):
    blocks = []
    L0_target, L0_min, L0_max, L0_overlap = 1500, 1000, 2000, 200
    lunch_box_size = 250
    
    start = 0
    while start < len(text):
        end = start + L0_target
        if end > len(text): end = len(text)
        else:
            # 자르는 위치 최적화: 마침표 등 우선 
            found = -1
            for p in [".", "!", "?", "\n"]:
                pos = text.rfind(p, start + L0_min, start + L0_max)
                if pos > found: found = pos
            if found != -1: end = found + 1
            elif (start + L0_max) < len(text): end = start + L0_max # 하드컷 

        body = text[start:end]
        prev_tail = text[max(0, start-lunch_box_size):start]
        next_head = text[end:end+lunch_box_size]
        
        blocks.append({
            "novel_id": novel_id,
            "level": "L0",
            "start_char": start,
            "end_char": end,
            "prev_tail": prev_tail,
            "body": body,
            "next_head": next_head
        })
        start = end - L0_overlap
        if end == len(text): break
    return blocks

def aggregate_staircase(l0_blocks):
    l1_blocks = [] # L1: group 3, stride 2 
    for i in range(0, len(l0_blocks)-2, 2):
        group = l0_blocks[i:i+3]
        l1_blocks.append({
            "level": "L1",
            "body": "".join([b['body'] for b in group]),
            "l0_indices": [i, i+1, i+2]
        })
    
    l2_blocks = [] # L2: group 9~12, stride 6 
    for i in range(0, len(l0_blocks)-9, 6):
        group = l0_blocks[i:i+10] # 대략 10개 묶음
        l2_blocks.append({
            "level": "L2",
            "body": "".join([b['body'] for b in group]),
            "l0_indices": list(range(i, min(i+10, len(l0_blocks))))
        })
    return l1_blocks, l2_blocks

if __name__ == "__main__":
    # Test/Implementation Logic for SBL v2
    pass
