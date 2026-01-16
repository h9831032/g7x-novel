[MIGRATION_INTERFACE_V1]
1. run_numeric_truck_v1.py의 calc 함수는 TaskExecutor 인터페이스의 규격을 따름.
2. 다음 공정(REAL_WORK) 전환 시, calc 함수 내부만 os.path.getsize() 및 shutil.copy2()로 교체하면 8-Lane 병렬 엔진 재사용 가능.
3. receipt.jsonl 및 verify_report.json의 규격은 동일하게 유지하여 상위 모니터링 툴의 호환성 보장.
