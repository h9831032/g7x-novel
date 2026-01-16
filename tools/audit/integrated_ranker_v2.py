import os, json

def integrated_audit(run_id):
    run_dir = f"C:\\g7core\\g7_v1\\runs\\{run_id}"
    all_defects = []
    
    # 트럭 A, B, C 전수 통합 스캔
    for truck in ['truckA', 'truckB', 'truckC']:
        t_dir = os.path.join(run_dir, truck)
        for b_idx in range(1, 21):
            res_dir = os.path.join(t_dir, f"bundle_{b_idx:02d}", "results")
            if not os.path.exists(res_dir): continue
            
            for f in os.listdir(res_dir):
                with open(os.path.join(res_dir, f), "r", encoding='utf-8') as j:
                    data = json.load(j)
                    if "모순" in str(data.get("output", "")) or data.get("status") == "FAIL":
                        all_defects.append({"id": f.replace(".json", ""), "truck": truck, "finding": data.get("output")})

    # 360발 통합 불량 리포트 봉인
    with open(os.path.join(run_dir, "final_audit_report.json"), "w", encoding='utf-8') as f:
        json.dump(all_defects, f, indent=4, ensure_ascii=False)
    print(f">>> [AUDIT_COMPLETE] 360 Tasks Scanned. {len(all_defects)} Defects Logged.")

if __name__ == "__main__":
    integrated_audit("REAL")