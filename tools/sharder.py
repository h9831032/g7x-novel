import os, sys
def split_jsonl(file_path, output_dir, chunk_size_mb=25):
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    base_name = os.path.basename(file_path)
    part_num = 1
    current_size = 0
    f_out = open(os.path.join(output_dir, f"{base_name}.part{part_num}"), 'w', encoding='utf-8')
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            f_out.write(line)
            current_size += len(line.encode('utf-8'))
            if current_size > chunk_size_mb * 1024 * 1024:
                f_out.close()
                part_num += 1
                f_out = open(os.path.join(output_dir, f"{base_name}.part{part_num}"), 'w', encoding='utf-8')
                current_size = 0
    f_out.close()
    return part_num
