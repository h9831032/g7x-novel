"""
G7X REAL36 슬라이스 오더 생성기 v1
- UNIT_RULE: (3+3)_x6 = 36
- DAY 슬라이스 6개 + NIGHT 슬라이스 6개 생성
- 각 슬라이스는 6라인 (3+3)
"""

import sys
from pathlib import Path

def main():
    ssot_root = Path(r"C:\g7core\g7_v1")
    gptorder_dir = ssot_root / "GPTORDER"

    # 소스 파일 읽기
    source_file = gptorder_dir / "TEST_REAL36_VERIFY.txt"
    if not source_file.exists():
        print(f"[FAIL_FAST] Source file not found: {source_file}")
        print(f"[NEXT_1] Create TEST_REAL36_VERIFY.txt with 36 mission lines")
        sys.exit(1)

    with open(source_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) != 36:
        print(f"[FAIL_FAST] Expected 36 missions, found {len(lines)}")
        print(f"[NEXT_1] Verify TEST_REAL36_VERIFY.txt has exactly 36 lines")
        sys.exit(1)

    # 슬라이스 생성 (각 6라인 = 3+3)
    slice_size = 6
    num_slices = 6

    # DAY 슬라이스 생성
    for i in range(num_slices):
        start_idx = i * slice_size
        end_idx = start_idx + slice_size
        slice_lines = lines[start_idx:end_idx]

        day_file = gptorder_dir / f"REAL36_DAY_S{i+1}.txt"
        with open(day_file, "w", encoding="utf-8") as f:
            for line in slice_lines:
                f.write(line + "\n")

        print(f"[CREATED] {day_file} ({len(slice_lines)} lines)")

    # NIGHT 슬라이스 생성 (동일한 내용)
    for i in range(num_slices):
        start_idx = i * slice_size
        end_idx = start_idx + slice_size
        slice_lines = lines[start_idx:end_idx]

        night_file = gptorder_dir / f"REAL36_NIGHT_S{i+1}.txt"
        with open(night_file, "w", encoding="utf-8") as f:
            for line in slice_lines:
                f.write(line + "\n")

        print(f"[CREATED] {night_file} ({len(slice_lines)} lines)")

    print(f"[SUCCESS] Generated 12 slice files (6 DAY + 6 NIGHT)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
