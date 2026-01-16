import os, shutil
def move_to_reissue(file_path, base_root, reason):
    reissue_dir = os.path.join(base_root, 'queue', 'reissue')
    os.makedirs(reissue_dir, exist_ok=True)
    filename = os.path.basename(file_path)
    try:
        shutil.move(file_path, os.path.join(reissue_dir, filename))
        print(f'[REISSUE] {filename} -> {reissue_dir} (Reason: {reason})')
        return True
    except Exception as e:
        print(f'[ERROR] Move failed: {e}')
        return False
