import os, sys, json, glob, time
from concurrent.futures import ThreadPoolExecutor

def run_engine():
    truck_id = sys.argv[1] if len(sys.argv) > 1 else "F"
    run_root = sys.argv[2] if len(sys.argv) > 2 else "C:\\g7core\\g7_v1\\runs\\REAL"
    
    truck_path = os.path.join(run_root, f"truck{truck_id}")
    res_dir = os.path.join(truck_path, "FINAL_RESULTS")
    os.makedirs(res_dir, exist_ok=True) # 물리 경로 강제 생성

    # [ACTION] 12발 스모크 태스크 생성
    tasks = [f"task_{truck_id}_{i:03d}" for i in range(1, 13)]
    
    def process(tid):
        # [FAIL_SWITCH] F_007 강제 실패 (재발주 시에는 통과되도록 설계)
        if tid == "task_F_007" and "--from_reissue_packet" not in str(sys.argv):
            raise RuntimeError("FAIL_TRIGGER")
        
        # 파일 물리 쓰기
        with open(os.path.join(res_dir, f"{tid}.json"), "w") as f:
            json.dump({"id": tid, "status": "PASS"}, f)
        return True

    print(f">>> [ENGINE] Truck {truck_id} 가공 시작 (Workers=3)")
    with ThreadPoolExecutor(max_workers=3) as executor:
        for t in tasks:
            try: executor.submit(process, t)
            except: pass
    
    time.sleep(1) # 쓰기 지연 방지
    
    # [ACTION] 감리 보고서 생성
    files = glob.glob(os.path.join(res_dir, "*.json"))
    report = {
        "expected_tasks": 12,
        "success_tasks": len(files),
        "physical_json_count": len(files),
        "physical_count_ok": len(files) == 12
    }
    with open(os.path.join(truck_path, "verify_report.json"), "w", encoding='utf-8') as f:
        json.dump(report, f, indent=4)
    print(f">>> [SUCCESS] {len(files)}개 파일 적재 및 보고서 생성 완료.")

if __name__ == "__main__":
    run_engine()