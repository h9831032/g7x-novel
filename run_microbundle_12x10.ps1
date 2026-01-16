# [G7X] V32.3 ARGUMENT_PRIORITY_REPAIR
$ErrorActionPreference = "Stop"
$SSOT_ROOT = "C:\g7core\g7_v1"; $LEGACY = "C:\g6core\g6_v24"

# [1] 인자 처리 보강 (인자 우선 원칙)
$RUN_ID = if ($args[0]) { $args[0] } else { "RUN_$(Get-Date -Format 'HHmm')" }
$T_ID = if ($args[1]) { $args[1] } else { "A" }
$PACKET_PATH = if ($args[2]) { $args[2] } else { "$SSOT_ROOT\packet_$T_ID.jsonl" }
$INNER_PATH = if ($args[3]) { $args[3] } else { "$SSOT_ROOT\engine\inner_engine_v1.py" }

function Save-Snapshot($path) { Get-ChildItem -Path $LEGACY -File -Recurse | Select-Object FullName, Length, LastWriteTime | Export-Csv -Path $path -NoTypeInformation }

try {
    # [2] 실행 전 실물 체크 (FAIL_FAST)
    if (-not (Test-Path $PACKET_PATH)) {
        Write-Host "!!! [FAIL_FAST] PACKET_PATH NOT FOUND: $PACKET_PATH" -ForegroundColor Red
        Write-Host ">>> Current Warehouse Status (dir):" -ForegroundColor Gray
        dir "$SSOT_ROOT\packet_*.jsonl"
        throw "ABORT: Target packet file is missing at the specified path."
    }

    Write-Host ">>> [G7X] Starting Truck $T_ID - REAL 12x10 EXECUTION..." -ForegroundColor Yellow
    
    # [3] Python 호출 시 명확한 경로 변수 전달
    cmd /c "python `"$SSOT_ROOT\engine\micro_bundle_runner_v1.py`" `"$RUN_ID`" `"$PACKET_PATH`" `"$T_ID`" `"$INNER_PATH`""
    if ($LASTEXITCODE -ne 0) { throw "Runner failed (Code: $LASTEXITCODE)" }

    cmd /c "python `"$SSOT_ROOT\engine\micro_bundle_verify_v1.py`" `"$RUN_ID`" `"$T_ID`""
    if ($LASTEXITCODE -ne 0) { throw "Verifier failed (Code: $LASTEXITCODE)" }

    # 최종 성공 판정
    $ReportPath = "$SSOT_ROOT\runs\$RUN_ID\truck$T_ID\FINAL\truck_verify_report.json"
    if (Test-Path $ReportPath) {
        $Final = Get-Content $ReportPath | ConvertFrom-Json
        if ($Final.pass_seal -eq $true) {
            Write-Host "`n>>> [SUCCESS] REAL 12x10 DEPLOYED & SEALED (Truck $T_ID)." -ForegroundColor Green
        } else { throw "FINAL_AUDIT_REJECTED" }
    } else { throw "MISSING_FINAL_REPORT" }

} catch {
    Write-Host "`n!!! [CRITICAL_FAIL] $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Write-Host "`n--- FINAL AUDIT CHECK ---"
    $ExitPath = "$SSOT_ROOT\runs\$RUN_ID\truck$T_ID\FINAL\exitcode.txt"
    if (Test-Path $ExitPath) {
        Write-Host "EXITCODE: $(Get-Content $ExitPath)"
    } else {
        Write-Host "NO EXITCODE FILE FOUND" -ForegroundColor Red
    }
    Read-Host "Audit Done"
}