import os, json, glob
from datetime import datetime
from engine.writer_adapter import WriterAdapter

class DevLogBuilder:
    def __init__(self, root, run_path):
        self.root = root
        self.run_path = run_path
        self.devlog_dir = os.path.join(root, "DEVLOG")
        os.makedirs(self.devlog_dir, exist_ok=True)

    def scan_environment(self):
        """최근 RUN 및 파일 변경 내역 스캔"""
        runs_dir = os.path.join(self.root, "runs")
        all_runs = sorted(glob.glob(os.path.join(runs_dir, "RUN_*")), key=os.path.getmtime, reverse=True)
        recent_runs = [os.path.basename(r) for r in all_runs[:3]]
        
        changed_files = []
        for dp, dn, filenames in os.walk(self.root):
            if "venv" in dp or ".git" in dp or "__pycache__" in dp: continue
            for f in filenames:
                fp = os.path.join(dp, f)
                try:
                    mtime = os.path.getmtime(fp)
                    changed_files.append((f, datetime.fromtimestamp(mtime).strftime('%H:%M:%S')))
                except: pass
        
        changed_files.sort(key=lambda x: x[1], reverse=True)
        return {"recent_runs": recent_runs, "files": changed_files[:15]}

    def generate_daily_log(self, config):
        # 1. 환경 스캔
        scan_data = self.scan_environment()
        
        # 2. AI 어댑터 점화
        adapter = WriterAdapter()
        
        # 3. 프롬프트 구성 (하청업체 보고 톤)
        prompt = f"""
        You are an AI Subcontractor Report System for project 'G7X'.
        Based on the system scan data below, generate a brief 'Daily Development Log' (DEVLOG).
        
        [SCAN DATA]
        - Recent Runs: {scan_data['recent_runs']}
        - Recently Modified Files: {scan_data['files']}
        - Current Task: {config}
        
        [REQUIREMENTS]
        - Tone: Strict, Professional, 'Subcontractor Report' style (Korean).
        - Structure:
          1. Summary of Activity
          2. Key Changes (Files modified)
          3. System Status (Runs)
        - Keep it concise (under 15 lines).
        - Start with "## [AI GENERATED REPORT]"
        """

        # 4. 진짜 생성 (Real Generation)
        result = adapter.generate(prompt)
        
        # 5. 결과 기록
        today = datetime.now().strftime("%Y%m%d")
        filename = f"DEVLOG_{today}.md"
        output_path = os.path.join(self.devlog_dir, filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# DEVLOG {today}\n")
            f.write(f"- Generated At: {datetime.now()}\n")
            f.write(f"- Model: {result.get('model', 'Unknown')}\n")
            f.write(f"- Latency: {result.get('latency_ms', 0)}ms\n")
            f.write(f"- Status: {result['status']}\n")
            f.write("-" * 40 + "\n")
            if result['status'] == "PASS":
                f.write(result['content'])
            else:
                f.write(f"ERROR: {result.get('error')}")
        
        return output_path