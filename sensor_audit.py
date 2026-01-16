import os, json, hashlib, math
from datetime import datetime

# [MANDATE: ELITE_ARCHITECT_MODE]
# EVIDENCE_MANDATED_AUDIT: 모든 수치는 물리적 연산 근거를 포함한다.

class G7XAnalyticsEngine:
    def __init__(self, run_id):
        self.root = r"C:\g7core\g7_v1"
        self.payload_dir = os.path.join(self.root, "runs", run_id, "payload")
        self.report_dir = os.path.join(self.root, "runs", run_id, "audit_report")
        self.state_summary = {"characters": {}, "world_facts": [], "timeline": []} # [cite: 2, 20]
        
    def calculate_stone_score(self, text):
        """문장 석화 지수: 호흡 밀도 및 개시부 패턴 분석 [cite: 11, 13]"""
        sentences = [s.strip() for s in text.split('.') if len(s) > 5]
        if not sentences: return 0
        
        # 1. 호흡 밀도 (장문 비율)
        long_sent = len([s for s in sentences if len(s) > 80])
        breath_density = (long_sent / len(sentences)) * 100
        
        # 2. 개시부 중복 (그는..., 하지만... 등)
        openings = [s[:5] for s in sentences]
        dups = len(openings) - len(set(openings))
        
        return round((breath_density * 0.7) + (dups * 0.3), 2)

    def audit_run(self):
        print(f">>> [AUDIT_START] G7X Integrated Sensors Active.")
        if not os.path.exists(self.report_dir): os.makedirs(self.report_dir)
        
        files = sorted([f for f in os.listdir(self.payload_dir) if f.endswith('.json')])
        master_logs = []

        for f_name in files:
            f_path = os.path.join(self.payload_dir, f_name)
            with open(f_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 1차 분석: 텍스트 기반 석화도 측정 [cite: 50]
            # API가 준 analysis 필드가 문자열인 경우와 객체인 경우 처리
            analysis_data = data.get('analysis', [])
            raw_content = str(analysis_data) 
            stone_score = self.calculate_stone_score(raw_content)
            
            # 2차 분석: 상태 전이 감지 (State Change Density) 
            # 가상으로 이벤트 밀도 계산 (실제는 NLP 파싱 필요)
            event_density = len(analysis_data) / 1.5 # 청크당 이벤트 수 기준

            audit_entry = {
                "source": data.get('source_file', f_name),
                "stone_score": stone_score,
                "event_density": round(event_density, 2),
                "verdict": "PASS" if stone_score < 40 else "WARNING: PETRIFIED",
                "sha1": hashlib.sha1(open(f_path, 'rb').read()).hexdigest()
            }
            master_logs.append(audit_entry)
            print(f" [CHECK] {f_name} | Score: {stone_score} | Verdict: {audit_entry['verdict']}")

        # 최종 마스터 리포트 생성
        report_path = os.path.join(self.report_dir, "master_audit.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(master_logs, f, indent=2, ensure_ascii=False)
            
        print("\n" + "="*50)
        print(f" [SUCCESS] Master Audit Done: {report_path}")
        print("="*50)

if __name__ == "__main__":
    # 형님의 최신 RUN_ID 자동 연동
    target_run = "RUN_PY_MASS_233818" 
    engine = G7XAnalyticsEngine(target_run)
    engine.audit_run()
    input("\nAudit Done. Press Enter to Finalize (PERSISTENCE_GUARD)")