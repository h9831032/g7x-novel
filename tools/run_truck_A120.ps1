$ErrorActionPreference = "Stop"
$PYTHON = "C:\Users\00\PycharmProjects\PythonProject\.venv\Scripts\python.exe"
$ROOT = "C:\g7core\g7_v1"
Write-Host ">>> A120 TRUCK START <<<" -ForegroundColor Cyan
& $PYTHON "$ROOT\main\manager.py" "REAL120_A.txt" 2>&1 | Tee-Object -FilePath "$ROOT\runs\latest_A.log"
if ($LASTEXITCODE -ne 0) { Write-Host "FAIL!" -ForegroundColor Red; Read-Host "Press Enter" }
