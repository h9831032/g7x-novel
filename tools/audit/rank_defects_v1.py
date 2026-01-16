import os
import json

def rank_defects_v2(run_id):
    run_dir = f"C:\\g7core\\g7_v1\\runs\\{run_id}"
    defects = []

    for truck in ['truckA', 'truckB']:
        truck_dir = os.path.join(run_dir, truck)
        for i in range(1, 21):
            bundle_res_dir = os.path.join(truck_dir, f"bundle_{i:02d}", "results")
            if not os.path.exists(bundle_res_dir): continue
            
            for file_name in os.listdir(bundle_res_dir):
                if not file_name.endswith(".json"): continue
                path = os.path.join(bundle_res_dir, file_name)
                
                with open(path, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    output_text = str(data.get("output", ""))
                    # [FIX] 파일명에서 ID 추출 및 모순 키워드 정밀 스캔
                    row_id = file_name.replace("task_", "").replace(".json", "")
                    
                    if "모순" in output_text or "FAIL" in data.get("status", ""):
                        defects.append({
                            "id": row_id,
                            "finding": output_text[:200] + "..." # 가독성을 위해 앞부분만 추출
                        })

    with open(os.path.join(run_dir, "defect_rank_report.json"), "w", encoding='utf-8') as f:
        json.dump(defects, f, indent=4, ensure_ascii=False)
    print(f">>> [SCAN_V2] 240 Tasks Re-Scanned. {len(defects)} Defects Identified.")

if __name__ == "__main__":
    rank_defects_v2("REAL")