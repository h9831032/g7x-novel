import os, json

def prep_real():
    root = r"C:\g7core\g7_v1"
    os.makedirs(os.path.join(root, "GPTORDER"), exist_ok=True)
    os.makedirs(os.path.join(root, "tools"), exist_ok=True)

    # 1. Catalog Update (Core 12 + Real 240 = 252 items)
    catalog = []
    # Core 12
    core_tasks = [
        ("BASIC_ENGINE_WELD_001", "Gate/Schema Validation", "main/gate.py"),
        ("BASIC_ENGINE_WELD_002", "Verifier Logic (SHA1)", "main/verifier.py"),
        ("BASIC_ENGINE_WELD_003", "Blackbox Logging", "engine/blackbox.py"),
        ("BASIC_ENGINE_WELD_004", "StampManifest", "engine/stamp.py"),
        ("BASIC_ENGINE_WELD_005", "VerifyReport", "main/report.py"),
        ("BASIC_ENGINE_WELD_006", "FinalAudit", "main/audit.py"),
        ("COST_GUARD_001", "Cost Guard", "engine/guard.py"),
        ("ANTI_TURBO_001", "Anti-Turbo", "engine/anti_turbo.py"),
        ("ORDER_LOCK_001", "Order Lock", "engine/lock.py"),
        ("RUN_WELD_001", "Run Welder", "tools/run_stable.ps1"),
        ("FAIL_BOX_001", "Fail Box", "engine/fail_box.py"),
        ("SMOKE3_PACK_001", "Smoke Pack", "tools/make_smoke3.ps1")
    ]
    for i, (cid, obj, out) in enumerate(core_tasks):
        catalog.append({"id": cid, "objective": obj, "outputs": out})
    
    # Real 240
    for i in range(1, 241):
        catalog.append({
            "id": f"REAL_{i:03d}",
            "objective": f"Real Task {i:03d}",
            "outputs": f"src/module_{i:03d}.py"
        })
    
    with open(os.path.join(root, "engine", "work_catalog_v1.json"), "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=4)

    # 2. GPTORDER Files
    with open(os.path.join(root, "GPTORDER", "REAL120_A.txt"), "w") as f:
        for i in range(1, 121): f.write(f"TASK_V2|payload=REAL_{i:03d}\n")
    
    with open(os.path.join(root, "GPTORDER", "REAL120_B.txt"), "w") as f:
        for i in range(121, 241): f.write(f"TASK_V2|payload=REAL_{i:03d}\n")

    # 3. PS1 Runners (With Output Capture & Pause)
    # A120
    ps_a = r'''$ErrorActionPreference = "Stop"
$PYTHON = "C:\Users\00\PycharmProjects\PythonProject\.venv\Scripts\python.exe"
$ROOT = "C:\g7core\g7_v1"
Write-Host ">>> A120 TRUCK START <<<" -ForegroundColor Cyan
& $PYTHON "$ROOT\main\manager.py" "REAL120_A.txt" 2>&1 | Tee-Object -FilePath "$ROOT\runs\latest_A.log"
if ($LASTEXITCODE -ne 0) { Write-Host "FAIL!" -ForegroundColor Red; Read-Host "Press Enter" }
'''
    with open(os.path.join(root, "tools", "run_truck_A120.ps1"), "w") as f: f.write(ps_a)

    # B120
    ps_b = r'''$ErrorActionPreference = "Stop"
$PYTHON = "C:\Users\00\PycharmProjects\PythonProject\.venv\Scripts\python.exe"
$ROOT = "C:\g7core\g7_v1"
Write-Host ">>> B120 TRUCK START <<<" -ForegroundColor Cyan
& $PYTHON "$ROOT\main\manager.py" "REAL120_B.txt" 2>&1 | Tee-Object -FilePath "$ROOT\runs\latest_B.log"
if ($LASTEXITCODE -ne 0) { Write-Host "FAIL!" -ForegroundColor Red; Read-Host "Press Enter" }
'''
    with open(os.path.join(root, "tools", "run_truck_B120.ps1"), "w") as f: f.write(ps_b)

    print("[SUCCESS] Full Catalog(252) & Runners Ready.")

if __name__ == "__main__":
    prep_real()