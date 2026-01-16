import os, shutil, json, time

class FailBox:
    def __init__(self, root=r"C:\g7core\g7_v1"):
        self.root = root
        self.box_dir = os.path.join(self.root, "runs", "FAIL_BOX")
        os.makedirs(self.box_dir, exist_ok=True)

    def quarantine(self, run_path, reason_code="UNKNOWN"):
        run_id = os.path.basename(run_path)
        dest = os.path.join(self.box_dir, run_id)
        
        # 격리 (Move)
        if os.path.exists(dest): shutil.rmtree(dest) # 중복 시 덮어쓰기
        shutil.move(run_path, dest)
        
        # 사유 기록
        with open(os.path.join(dest, "fail_reason.json"), "w", encoding="utf-8") as f:
            json.dump({"run_id": run_id, "reason": reason_code, "ts": time.time()}, f, indent=4)
        
        print(f"   [FAIL_BOX] Quarantined: {run_id} (Reason: {reason_code})")

# [PHASE3_WELD] box01_half2_seq001 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq001
# TIMESTAMP: 2026-01-10 22:45:29.115477

# [PHASE3_WELD] box01_half2_seq002 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq002
# TIMESTAMP: 2026-01-10 22:45:30.224127

# [PHASE3_WELD] box01_half2_seq003 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq003
# TIMESTAMP: 2026-01-10 22:45:31.342601

# [PHASE3_WELD] box01_half2_seq004 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq004
# TIMESTAMP: 2026-01-10 22:45:32.455952

# [PHASE3_WELD] box01_half2_seq005 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq005
# TIMESTAMP: 2026-01-10 22:45:33.574958

# [PHASE3_WELD] box01_half2_seq006 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq006
# TIMESTAMP: 2026-01-10 22:45:34.697604

# [PHASE3_WELD] box01_half2_seq007 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq007
# TIMESTAMP: 2026-01-10 22:45:35.819182

# [PHASE3_WELD] box01_half2_seq008 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq008
# TIMESTAMP: 2026-01-10 22:45:36.931880

# [PHASE3_WELD] box01_half2_seq009 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq009
# TIMESTAMP: 2026-01-10 22:45:38.046208

# [PHASE3_WELD] box01_half2_seq010 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq010
# TIMESTAMP: 2026-01-10 22:45:39.164106

# [PHASE3_WELD] box01_half2_seq011 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq011
# TIMESTAMP: 2026-01-10 22:45:40.287103

# [PHASE3_WELD] box01_half2_seq012 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq012
# TIMESTAMP: 2026-01-10 22:45:41.408104

# [PHASE3_WELD] box01_half2_seq013 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq013
# TIMESTAMP: 2026-01-10 22:45:42.527136

# [PHASE3_WELD] box01_half2_seq014 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq014
# TIMESTAMP: 2026-01-10 22:45:43.650118

# [PHASE3_WELD] box01_half2_seq015 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq015
# TIMESTAMP: 2026-01-10 22:45:44.773110

# [PHASE3_WELD] box01_half2_seq016 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq016
# TIMESTAMP: 2026-01-10 22:45:45.895365

# [PHASE3_WELD] box01_half2_seq017 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq017
# TIMESTAMP: 2026-01-10 22:45:47.015096

# [PHASE3_WELD] box01_half2_seq018 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq018
# TIMESTAMP: 2026-01-10 22:45:48.134952

# [PHASE3_WELD] box01_half2_seq019 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq019
# TIMESTAMP: 2026-01-10 22:45:49.256311

# [PHASE3_WELD] box01_half2_seq020 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq020
# TIMESTAMP: 2026-01-10 22:45:50.379833

# [PHASE3_WELD] box01_half2_seq021 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq021
# TIMESTAMP: 2026-01-10 22:45:51.496445

# [PHASE3_WELD] box01_half2_seq022 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq022
# TIMESTAMP: 2026-01-10 22:45:52.622060

# [PHASE3_WELD] box01_half2_seq023 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq023
# TIMESTAMP: 2026-01-10 22:45:53.742433

# [PHASE3_WELD] box01_half2_seq024 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq024
# TIMESTAMP: 2026-01-10 22:45:54.863951

# [PHASE3_WELD] box01_half2_seq025 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq025
# TIMESTAMP: 2026-01-10 22:45:55.988927

# [PHASE3_WELD] box01_half2_seq026 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq026
# TIMESTAMP: 2026-01-10 22:45:57.110319

# [PHASE3_WELD] box01_half2_seq027 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq027
# TIMESTAMP: 2026-01-10 22:45:58.232590

# [PHASE3_WELD] box01_half2_seq028 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq028
# TIMESTAMP: 2026-01-10 22:45:59.348332

# [PHASE3_WELD] box01_half2_seq029 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq029
# TIMESTAMP: 2026-01-10 22:46:00.459246

# [PHASE3_WELD] box01_half2_seq030 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq030
# TIMESTAMP: 2026-01-10 22:46:01.574522

# [PHASE3_WELD] box01_half2_seq031 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq031
# TIMESTAMP: 2026-01-10 22:46:02.689423

# [PHASE3_WELD] box01_half2_seq032 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq032
# TIMESTAMP: 2026-01-10 22:46:03.813101

# [PHASE3_WELD] box01_half2_seq033 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq033
# TIMESTAMP: 2026-01-10 22:46:04.937332

# [PHASE3_WELD] box01_half2_seq034 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq034
# TIMESTAMP: 2026-01-10 22:46:06.052935

# [PHASE3_WELD] box01_half2_seq035 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq035
# TIMESTAMP: 2026-01-10 22:46:07.172051

# [PHASE3_WELD] box01_half2_seq036 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq036
# TIMESTAMP: 2026-01-10 22:46:08.296901

# [PHASE3_WELD] box01_half2_seq037 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq037
# TIMESTAMP: 2026-01-10 22:46:09.417713

# [PHASE3_WELD] box01_half2_seq038 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq038
# TIMESTAMP: 2026-01-10 22:46:10.534081

# [PHASE3_WELD] box01_half2_seq039 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq039
# TIMESTAMP: 2026-01-10 22:46:11.648574

# [PHASE3_WELD] box01_half2_seq040 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq040
# TIMESTAMP: 2026-01-10 22:46:12.773134

# [PHASE3_WELD] box01_half2_seq041 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq041
# TIMESTAMP: 2026-01-10 22:46:13.891967

# [PHASE3_WELD] box01_half2_seq042 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq042
# TIMESTAMP: 2026-01-10 22:46:15.011427

# [PHASE3_WELD] box01_half2_seq043 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq043
# TIMESTAMP: 2026-01-10 22:46:16.123952

# [PHASE3_WELD] box01_half2_seq044 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq044
# TIMESTAMP: 2026-01-10 22:46:17.237853

# [PHASE3_WELD] box01_half2_seq045 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq045
# TIMESTAMP: 2026-01-10 22:46:18.359163

# [PHASE3_WELD] box01_half2_seq046 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq046
# TIMESTAMP: 2026-01-10 22:46:19.485039

# [PHASE3_WELD] box01_half2_seq047 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq047
# TIMESTAMP: 2026-01-10 22:46:20.610544

# [PHASE3_WELD] box01_half2_seq048 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq048
# TIMESTAMP: 2026-01-10 22:46:21.731643

# [PHASE3_WELD] box01_half2_seq049 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq049
# TIMESTAMP: 2026-01-10 22:46:22.847880

# [PHASE3_WELD] box01_half2_seq050 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq050
# TIMESTAMP: 2026-01-10 22:46:23.966954

# [PHASE3_WELD] box01_half2_seq051 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq051
# TIMESTAMP: 2026-01-10 22:46:25.084963

# [PHASE3_WELD] box01_half2_seq052 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq052
# TIMESTAMP: 2026-01-10 22:46:26.197799

# [PHASE3_WELD] box01_half2_seq053 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq053
# TIMESTAMP: 2026-01-10 22:46:27.315953

# [PHASE3_WELD] box01_half2_seq054 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq054
# TIMESTAMP: 2026-01-10 22:46:28.434952

# [PHASE3_WELD] box01_half2_seq055 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq055
# TIMESTAMP: 2026-01-10 22:46:29.550329

# [PHASE3_WELD] box01_half2_seq056 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq056
# TIMESTAMP: 2026-01-10 22:46:30.670606

# [PHASE3_WELD] box01_half2_seq057 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq057
# TIMESTAMP: 2026-01-10 22:46:31.794383

# [PHASE3_WELD] box01_half2_seq058 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq058
# TIMESTAMP: 2026-01-10 22:46:32.910198

# [PHASE3_WELD] box01_half2_seq059 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq059
# TIMESTAMP: 2026-01-10 22:46:34.033241

# [PHASE3_WELD] box01_half2_seq060 | FAILBOX_REQUEUE_PROOF
# OBJECTIVE: Update engine/failbox.py to handle automated isolation for task box01_half2_seq060
# TIMESTAMP: 2026-01-10 22:46:35.156573

# [G7X_PHASE3_WELD] box01_half2_seq001 | 2026-01-10 23:26:06.251907

# [G7X_PHASE3_WELD] box01_half2_seq002 | 2026-01-10 23:26:07.364190

# [G7X_PHASE3_WELD] box01_half2_seq003 | 2026-01-10 23:26:08.483951

# [G7X_PHASE3_WELD] box01_half2_seq004 | 2026-01-10 23:26:09.595897

# [G7X_PHASE3_WELD] box01_half2_seq005 | 2026-01-10 23:26:10.709155

# [G7X_PHASE3_WELD] box01_half2_seq006 | 2026-01-10 23:26:11.825942

# [G7X_PHASE3_WELD] box01_half2_seq007 | 2026-01-10 23:26:12.943149

# [G7X_PHASE3_WELD] box01_half2_seq008 | 2026-01-10 23:26:14.057509

# [G7X_PHASE3_WELD] box01_half2_seq009 | 2026-01-10 23:26:15.174266

# [G7X_PHASE3_WELD] box01_half2_seq010 | 2026-01-10 23:26:16.289111

# [G7X_PHASE3_WELD] box01_half2_seq011 | 2026-01-10 23:26:17.399114

# [G7X_PHASE3_WELD] box01_half2_seq012 | 2026-01-10 23:26:18.517421

# [G7X_PHASE3_WELD] box01_half2_seq013 | 2026-01-10 23:26:19.630091

# [G7X_PHASE3_WELD] box01_half2_seq014 | 2026-01-10 23:26:20.746863

# [G7X_PHASE3_WELD] box01_half2_seq015 | 2026-01-10 23:26:21.862661

# [G7X_PHASE3_WELD] box01_half2_seq016 | 2026-01-10 23:26:22.980070

# [G7X_PHASE3_WELD] box01_half2_seq017 | 2026-01-10 23:26:24.097238

# [G7X_PHASE3_WELD] box01_half2_seq018 | 2026-01-10 23:26:25.205854

# [G7X_PHASE3_WELD] box01_half2_seq019 | 2026-01-10 23:26:26.329856

# [G7X_PHASE3_WELD] box01_half2_seq020 | 2026-01-10 23:26:27.441210

# [G7X_PHASE3_WELD] box01_half2_seq021 | 2026-01-10 23:26:28.557562

# [G7X_PHASE3_WELD] box01_half2_seq022 | 2026-01-10 23:26:29.671023

# [G7X_PHASE3_WELD] box01_half2_seq023 | 2026-01-10 23:26:30.791181

# [G7X_PHASE3_WELD] box01_half2_seq024 | 2026-01-10 23:26:31.915001

# [G7X_PHASE3_WELD] box01_half2_seq025 | 2026-01-10 23:26:33.032828

# [G7X_PHASE3_WELD] box01_half2_seq026 | 2026-01-10 23:26:34.149982

# [G7X_PHASE3_WELD] box01_half2_seq027 | 2026-01-10 23:26:35.272978

# [G7X_PHASE3_WELD] box01_half2_seq028 | 2026-01-10 23:26:36.393908

# [G7X_PHASE3_WELD] box01_half2_seq029 | 2026-01-10 23:26:37.514140

# [G7X_PHASE3_WELD] box01_half2_seq030 | 2026-01-10 23:26:38.632937

# [G7X_PHASE3_WELD] box01_half2_seq031 | 2026-01-10 23:26:39.750943

# [G7X_PHASE3_WELD] box01_half2_seq032 | 2026-01-10 23:26:40.871943

# [G7X_PHASE3_WELD] box01_half2_seq033 | 2026-01-10 23:26:41.990967

# [G7X_PHASE3_WELD] box01_half2_seq034 | 2026-01-10 23:26:43.107833

# [G7X_PHASE3_WELD] box01_half2_seq035 | 2026-01-10 23:26:44.220910

# [G7X_PHASE3_WELD] box01_half2_seq036 | 2026-01-10 23:26:45.337907

# [G7X_PHASE3_WELD] box01_half2_seq037 | 2026-01-10 23:26:46.456710

# [G7X_PHASE3_WELD] box01_half2_seq038 | 2026-01-10 23:26:47.575064

# [G7X_PHASE3_WELD] box01_half2_seq039 | 2026-01-10 23:26:48.696564

# [G7X_PHASE3_WELD] box01_half2_seq040 | 2026-01-10 23:26:49.811875

# [G7X_PHASE3_WELD] box01_half2_seq041 | 2026-01-10 23:26:50.932048

# [G7X_PHASE3_WELD] box01_half2_seq042 | 2026-01-10 23:26:52.048234

# [G7X_PHASE3_WELD] box01_half2_seq043 | 2026-01-10 23:26:53.171617

# [G7X_PHASE3_WELD] box01_half2_seq044 | 2026-01-10 23:26:54.291836

# [G7X_PHASE3_WELD] box01_half2_seq045 | 2026-01-10 23:26:55.413950

# [G7X_PHASE3_WELD] box01_half2_seq046 | 2026-01-10 23:26:56.533951

# [G7X_PHASE3_WELD] box01_half2_seq047 | 2026-01-10 23:26:57.649809

# [G7X_PHASE3_WELD] box01_half2_seq048 | 2026-01-10 23:26:58.769285

# [G7X_PHASE3_WELD] box01_half2_seq049 | 2026-01-10 23:26:59.888644

# [G7X_PHASE3_WELD] box01_half2_seq050 | 2026-01-10 23:27:01.003952

# [G7X_PHASE3_WELD] box01_half2_seq051 | 2026-01-10 23:27:02.123951

# [G7X_PHASE3_WELD] box01_half2_seq052 | 2026-01-10 23:27:03.247176

# [G7X_PHASE3_WELD] box01_half2_seq053 | 2026-01-10 23:27:04.369759

# [G7X_PHASE3_WELD] box01_half2_seq054 | 2026-01-10 23:27:05.487965

# [G7X_PHASE3_WELD] box01_half2_seq055 | 2026-01-10 23:27:06.603963

# [G7X_PHASE3_WELD] box01_half2_seq056 | 2026-01-10 23:27:07.719733

# [G7X_PHASE3_WELD] box01_half2_seq057 | 2026-01-10 23:27:08.836207

# [G7X_PHASE3_WELD] box01_half2_seq058 | 2026-01-10 23:27:09.956906

# [G7X_PHASE3_WELD] box01_half2_seq059 | 2026-01-10 23:27:11.075953

# [G7X_PHASE3_WELD] box01_half2_seq060 | 2026-01-10 23:27:12.189908
