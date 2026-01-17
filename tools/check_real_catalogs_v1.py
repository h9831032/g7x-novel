"""
G7X Real Catalog Sanity Check v1
- REAL12/REAL24/REAL36 카탈로그 파일 검증
- 줄수, 빈줄, 중복 검사
"""

import sys
from pathlib import Path

def check_catalog(file_path, expected_lines):
    """카탈로그 파일 검증"""
    if not file_path.exists():
        print(f"  ✗ {file_path.name}: FILE NOT FOUND")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 전체 줄수
    total_lines = len(lines)

    # 빈줄이 아닌 줄
    non_empty_lines = [line.strip() for line in lines if line.strip()]

    # 중복 체크
    duplicates = len(non_empty_lines) - len(set(non_empty_lines))

    # 검증
    issues = []

    if len(non_empty_lines) != expected_lines:
        issues.append(f"Expected {expected_lines} lines, found {len(non_empty_lines)}")

    if duplicates > 0:
        issues.append(f"Found {duplicates} duplicate missions")

    if issues:
        print(f"  ✗ {file_path.name}:")
        for issue in issues:
            print(f"    - {issue}")
        return False
    else:
        print(f"  ✓ {file_path.name}: OK ({len(non_empty_lines)} missions)")
        return True

def main():
    ssot_root = Path(r"C:\g7core\g7_v1")
    gptorder_dir = ssot_root / "GPTORDER"

    print("[CATALOG SANITY CHECK]")
    print("")

    catalogs = [
        ("TEST_REAL12_VERIFY.txt", 12),
        ("REAL24_REAL_A.txt", 24),
        ("REAL36_REAL_A.txt", 36),
    ]

    all_passed = True

    for catalog_name, expected_lines in catalogs:
        catalog_path = gptorder_dir / catalog_name
        passed = check_catalog(catalog_path, expected_lines)
        if not passed:
            all_passed = False

    print("")

    if all_passed:
        print("[SUCCESS] All catalogs passed sanity check")
        return 0
    else:
        print("[FAIL] Some catalogs failed sanity check")
        return 1

if __name__ == "__main__":
    sys.exit(main())
