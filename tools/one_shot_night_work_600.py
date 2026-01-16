from __future__ import annotations
import os, subprocess, sys
from pathlib import Path

ROOT = Path(r'C:\g7core\g7_v1')
PY = sys.executable

def main():
    builder = ROOT / 'tools' / 'build_work_catalog_v3.py'
    queue = ROOT / 'GPTORDER' / 'NIGHT_QUEUE_WORK_600.txt'
    guard = ROOT / 'main' / 'night_shift_guard_v5.py'

    if not builder.exists():
        print('[FAIL] missing builder', str(builder))
        return 1

    print('>>> [STEP 1] Building Catalog...')
    r1 = subprocess.run([PY, str(builder)])
    if r1.returncode != 0:
        print('[FAIL] builder returncode', r1.returncode)
        return r1.returncode

    if not queue.exists():
        print('[FAIL] missing queue', str(queue))
        return 1

    print('>>> [STEP 2] Launching Guard Engine...')
    r2 = subprocess.run([PY, str(guard), '--queue', str(queue)])
    print('>>> [GUARD_RETURN]', r2.returncode)
    return r2.returncode

if __name__ == '__main__':
    raise SystemExit(main())
