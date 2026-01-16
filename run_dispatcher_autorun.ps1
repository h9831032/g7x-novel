# [G7X] V34.0 AUTORUN_DISPATCHER (PERSISTENCE_GUARD 적용)
$ErrorActionPreference = "Stop"
${SSOT_ROOT} = "C:\g7core\g7_v1"

# 1. 인자 처리
${BACKLOG_PATH} = if ($args[0]) { $args[0] } else { "${SSOT_ROOT}\오늘일정.txt" }
${RUN_ID} = if ($args[1]) { $args[1] } else { "RUN_AUTO_$(Get-Date -Format 'MMdd_HHmm')" }

try {
    # 2. Backlog 파일이 없으면 더미라도 생성
    if (-not (Test-Path ${BACKLOG_PATH})) {
        "Default Inspection Task`nRefactoring Task" | Out-File -FilePath ${BACKLOG_PATH} -Encoding utf8
        Write-Host ">>> [INFO] Created dummy backlog at ${BACKLOG_PATH}" -ForegroundColor Gray
    }

    Write-Host "`n>>> [1/4] Compiling Backlog to 240 Rounds..." -ForegroundColor Yellow
    python "${SSOT_ROOT}\tools\backlog_compiler_v1.py" "${BACKLOG_PATH}"

    # 3. 트럭 A/B 순차 배차
    foreach (${T} in "A", "B") {
        Write-Host ">>> [2/4] Dispatching Truck ${T} (6x20 SERIAL)..." -ForegroundColor Yellow
        ${P} = "${SSOT_ROOT}\packet_${T}.jsonl"
        ${I} = "${SSOT_ROOT}\engine\inner_engine_v1.py"
        
        # 기존 6x20 ps1 호출
        .\run_microbundle_6x20.ps1 "${RUN_ID}" "${T}" "${P}" "${I}"
    }

    Write-Host "`n>>> [3/4] Generating Evidence Pack..." -ForegroundColor Yellow
    python "${SSOT_ROOT}\tools\evidence_pack_writer_v1.py" "${RUN_ID}"

    Write-Host "`n>>> [SUCCESS] OPERATION COMPLETED: ${RUN_ID}" -ForegroundColor Green

} catch {
    Write-Host "`n!!! [CRITICAL_FAIL] $(${_}.Exception.Message)" -ForegroundColor Red
} finally {
    Write-Host "`n========================================================="
    Read-Host "Audit Done (자동 배차 공정 종료)"
}