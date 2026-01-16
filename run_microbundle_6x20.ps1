# [G7X] V33.2 6x20 SERIAL_STABLE_CONTROL
$ErrorActionPreference = "Stop"
${SSOT_ROOT} = "C:\g7core\g7_v1"

${RUN_ID} = if ($args[0]) { $args[0] } else { "RUN_SEQ_$(Get-Date -Format 'HHmm')" }
${T_ID} = if ($args[1]) { $args[1] } else { "A" }
${PACKET} = if ($args[2]) { $args[2] } else { "${SSOT_ROOT}\packet_${T_ID}.jsonl" }
${INNER} = if ($args[3]) { $args[3] } else { "${SSOT_ROOT}\engine\inner_engine_v1.py" }

try {
    if (-not (Test-Path ${PACKET})) { throw "PACKET_NOT_FOUND: ${PACKET}" }

    Write-Host ">>> [G7X] Launching Truck ${T_ID} (6x20 SERIAL)..." -ForegroundColor Yellow
    
    # 1. Runner 실행
    cmd /c "python `"${SSOT_ROOT}\engine\micro_bundle_runner_v1.py`" `"${RUN_ID}`" `"${PACKET}`" `"${T_ID}`" `"${INNER}`""
    if ($LASTEXITCODE -ne 0) { throw "Runner failed. Check C:\g7core\g7_v1\logs\stderr.txt" }

    # 2. Verify 실행 (느낌표 제거 완료)
    cmd /c "python `"${SSOT_ROOT}\engine\micro_bundle_verify_v1.py`" `"${RUN_ID}`" `"${T_ID}`""
    if ($LASTEXITCODE -ne 0) { throw "Verifier failed." }

    Write-Host "`n>>> [SUCCESS] TRUCK ${T_ID}: 6x20 SERIAL SEALED." -ForegroundColor Green

} catch {
    Write-Host "`n!!! [CRITICAL_FAIL] $(${_}.Exception.Message)" -ForegroundColor Red
} finally {
    Write-Host "`n========================================================="
    Read-Host "Audit Done"
}