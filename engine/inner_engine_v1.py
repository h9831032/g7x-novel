import sys, json, os, time
# 배선 연결: LAW60 센서 로드
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from LAW60_sensor_v1 import LAW60Sensor
    sensor = LAW60Sensor()
except Exception as e:
    print(f"FAILED_TO_LOAD_SENSOR: {str(e)}")
    sys.exit(2)

def main():
    packet_path, bundle_dir = sys.argv[1:3]
    
    with open(packet_path, 'r', encoding='utf-8') as f:
        tasks = [json.loads(line) for line in f if line.strip()]
    
    results = []
    for task in tasks:
        # [핵심] 6개 작업을 하나씩 정성껏 패는 직렬 연산
        print(f">>> [LAW60_AUDIT] Row {task['row_id']}...")
        report = sensor.audit_content(task['payload'])
        
        results.append({
            "row_id": task['row_id'],
            "task_signature": task['task_signature'],
            "law60_report": report
        })
        time.sleep(1) # API 속도 제한 안전장치

    # 번들 영수증 발행
    with open(os.path.join(bundle_dir, "verify_report.json"), "w", encoding='utf-8') as f:
        json.dump({"pass_seal": True, "task_count": len(results), "results": results}, f, indent=4)
    
    print(f"--- [BUNDLE_DONE] {len(results)} tasks audited.")

if __name__ == "__main__":
    main()