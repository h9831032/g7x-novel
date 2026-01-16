from __future__ import annotations
import json, time
from pathlib import Path

def ensure_blackbox(run_dir: str) -> str:
    run = Path(run_dir)
    bb = run / 'blackbox_log.jsonl'
    if bb.exists() and bb.stat().st_size > 0:
        return str(bb)
    run.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    rec_dir = run / 'receipts' / 'mission'
    rec_cnt = len(list(rec_dir.glob('*.json'))) if rec_dir.exists() else 0
    req = ['verify_report.json','stamp_manifest.json','final_audit.json','exitcode.txt']
    req_state = {k: (run / k).exists() for k in req}
    events = []
    events.append({'ts': ts, 'event': 'BACKFILL_START', 'run': str(run)})
    events.append({'ts': ts, 'event': 'BACKFILL_SNAPSHOT', 'receipts': rec_cnt, 'req': req_state})
    events.append({'ts': ts, 'event': 'BACKFILL_END'})
    with bb.open('w', encoding='utf-8') as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')
    return str(bb)
