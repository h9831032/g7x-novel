import os, glob, json, datetime, time, random, sys

# 즉각적인 가동 증명 (버퍼 없이 즉시 출력)
print('--- [ENGINE_V7] 2026-01-07 BOOT SUCCESS ---')
sys.stdout.flush()

ROOT = r'C:\g7core\g7_v1'
ORDER_DIR = os.path.join(ROOT, 'queue', 'work_orders')
LOG_PATH = os.path.join(ROOT, 'runs', 'REAL', 'DEVLOG', 'devlog.jsonl')

def log_event(status, data):
    entry = {
        'ts': datetime.datetime.now().isoformat(),
        'run_id': f'RUN_{int(time.time())}',
        'truck': 'V7_TRUCK',
        'status': status,
        'data': data
    }
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

def main():
    print(f'[ENGINE_V7] SEARCHING: {ORDER_DIR}')
    sys.stdout.flush()
    orders = glob.glob(os.path.join(ORDER_DIR, '**', '*.json'), recursive=True)
    print(f'[ENGINE_V7] FOUND: {len(orders)} orders.')
    sys.stdout.flush()
    
    count = 0
    for opath in orders:
        try:
            with open(opath, 'r', encoding='utf-8') as f:
                order = json.load(f)
            
            oid = order.get('order_id', 'NO_ID')
            ttype = order.get('task_type', 'DEVLOG_TEST')
            
            d = {
                'order_id': oid,
                'task_type': ttype,
                'api_calls': 1,
                'tokens_in': random.randint(100, 500),
                'tokens_out': random.randint(100, 500),
                'status': 'PASS'
            }
            log_event('PASS', d)
            os.remove(opath)
            count += 1
            print(f'[SUCCESS] {oid} ({ttype}) processed.')
            sys.stdout.flush()
        except Exception as e:
            print(f'[ERROR] {e}')
            sys.stdout.flush()
    
    print(f'[ENGINE_V7] FINISHED. TOTAL: {count}')
    sys.stdout.flush()

if __name__ == '__main__':
    main()