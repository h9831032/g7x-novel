import os
import json
import hashlib
from pathlib import Path

def scan_chunks(input_dir):
    inventory = []
    # 실제 파일 시스템 스캔
    for root, dirs, files in os.walk(input_dir):
        for f in files:
            if f.endswith('.txt'):
                full_path = os.path.join(root, f)
                size = os.path.getsize(full_path)
                if size < 100: continue # 너무 작은 파일 스킵
                
                # WID 추출 (파일명 규격: WID-Hash.txt 가정, 없으면 폴더명 사용)
                wid = f.split('-')[0] if '-' in f else os.path.basename(root)
                inventory.append({"wid": wid, "path": full_path, "size": size})
    return inventory

if __name__ == "__main__":
    data = scan_chunks(r'C:\g6core\g6_v24\data\umr\chunks')
    with open('inventory_temp.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Inventory Scanned: {len(data)} chunks found.")
