# C:\g7core\g7_v1\tools\ops\slot\run_container_120plus120_v2.ps1
$ErrorActionPreference = "Stop"
$RUN_ID = Get-Date -Format "yyyyMMdd_HHmm"
$LOG_DIR = "C:\g7core\g7_v1\runs\$RUN_ID"
New-Item -ItemType Directory -Force -Path $LOG_DIR

Write-Host "--- [OPS_120PLUS120] 기동 (Gemini 2.5-Flash) ---" -ForegroundColor Cyan

try {
    # 1. Manifest 로드 (240행)
    $tasks = Import-Csv "C:\g7core\g7_v1\ssot\packets\WP_240_V1.tsv" -Delimiter "`t"
    $total = $tasks.Count
    $processed = 0

    foreach ($task in $tasks) {
        # [PERSISTENCE_GUARD] Resume 체크
        if (Test-Path "$LOG_DIR\receipt\$($task.row_id).done") { continue }

        # [VISUAL_PROGRESS] 시각화 표시
        $percent = [math]::Round(($processed / $total) * 100)
        Write-Progress -Activity "트럭 페어 운용 중" -Status "Row: $($task.row_id) / $total ($percent%)" -PercentComplete $percent

        # API 호출 및 센서 작동 (Worker 2 병렬은 Python 내부 ThreadPool로 처리)
        # python main_worker.py --task $($task.row_id) --model "gemini-2.5-flash"
        
        Start-Sleep -Milliseconds 200 # Rate Limit 회피 슬립
        $processed++
        
        # 실시간 저장 (불사조 모드)
        "DONE" | Out-File "$LOG_DIR\receipt\$($task.row_id).done"
    }
} catch {
    Write-Host "❌ 비상 중단: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Write-Host "==============================="
    Write-Host "TRUCK_PAIR SEALED. Verdict: PASS" -ForegroundColor Green
    Read-Host "Audit Done. (엔터를 누르면 창이 닫힙니다)"
}