import os
def resolve_order_dir(base_root, target, mode):
    suffix = f'_{mode}'
    folder_name = f'{target}{suffix}'
    return os.path.normpath(os.path.join(base_root, 'queue', 'work_orders', folder_name))
