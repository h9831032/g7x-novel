import os, json
from datetime import datetime

class DevLogScheduler:
    def __init__(self, root, run_path):
        self.root = root
        self.run_path = run_path
        self.state_path = os.path.join(self.root, "runs", "STATE_PACK", "devlog_state.json")
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        self.load_state()

    def load_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, "r") as f: self.state = json.load(f)
        else:
            self.state = {"last_4h": None, "last_daily": None}

    def save_state(self):
        with open(self.state_path, "w") as f: json.dump(self.state, f)

    def tick(self, now_dt):
        created_files = []
        # 1. 4시간 주기 체크 (0, 4, 8, 12, 16, 20시)
        hour = now_dt.hour
        if hour % 4 == 0 and self.state["last_4h"] != hour:
            path = os.path.join(self.run_path, "devlog", f"devlog_4h_{now_dt.strftime('%Y%m%d_%H%M')}.json")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f: json.dump({"ts": str(now_dt), "msg": "4h snapshot"}, f)
            self.state["last_4h"] = hour
            created_files.append(path)

        # 2. 23:00 일일 리포트 체크
        if hour == 23 and self.state["last_daily"] != now_dt.date().isoformat():
            path = os.path.join(self.run_path, "reports", f"daily_{now_dt.strftime('%Y%m%d')}.md")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f: f.write(f"# Daily Report {now_dt.date()}\nSimulated Completion at 23:00.")
            self.state["last_daily"] = now_dt.date().isoformat()
            created_files.append(path)

        self.save_state()
        return created_files