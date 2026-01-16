param([string]$SOURCE_FILE)
$ErrorActionPreference = "Stop"
$SSOT_ROOT = "C:\g7core\g7_v1"

function Run-Sealed-Process([string]$RunName) {
    $RUN_DIR = Join-Path $SSOT_ROOT "runs\$RunName"
    New-Item -ItemType Directory -Force -Path $RUN_DIR | Out-Null
    
    $STDOUT_P = Join-Path $RUN_DIR "stdout.txt"
    $STDERR_P = Join-Path $RUN_DIR "stderr.txt"
    $EXIT_P = Join-Path $RUN_DIR "exitcode.txt"
    
    $t_start = Get-Date
    try {
        Write-Host "### [$RunName] IGNITION..." -ForegroundColor Cyan
        $RawStats = python "$SSOT_ROOT\tools\library_tagger_v1.py" $SOURCE_FILE $RUN_DIR 1>>$STDOUT_P 2>>$STDERR_P
        $Stats = $RawStats | ConvertFrom-Json
        
        # [A] DRIFT_LOCK 핵심 로직
        $pass_seal = $false
        $reasons = @()
        
        if ($Stats.drift_unresolved -eq 0 -and $Stats.errors -eq 0) {
            $pass_seal = $true
            $final_exit = 0
        } else {
            $pass_seal = $false
            $final_exit = 2
            if ($Stats.drift_unresolved -gt 0) { $reasons += "DRIFT_DETECTED_UNRESOLVED" }
            if ($Stats.errors -gt 0) { $reasons += "PROCESS_ERRORS_EXIST" }
        }

        # [B] verify_report.json 생성
        $Report = @{
            run_id = $RunName; source_root = $SOURCE_FILE; pass_seal = $pass_seal
            file_count = 1; chunk_count = $Stats.total; strike_count = 0
            drift_unresolved = $Stats.drift_unresolved; reasons_if_fail = $reasons
            timings = @{ total_sec = ((Get-Date) - $t_start).TotalSeconds }
        }
        $Report | ConvertTo-Json | Out-File (Join-Path $RUN_DIR "verify_report.json") -Encoding utf8
        "$final_exit" | Out-File $EXIT_P -Force
        
        # [C] hash_manifest.json 생성 (자기 자신 포함 2단계 봉인)
        $Manifest = @{ files = @{} }
        $Targets = "library_index.jsonl", "audit_receipt.jsonl", "verify_report.json", "exitcode.txt", "stdout.txt"
        foreach ($f in $Targets) {
            $p = Join-Path $RUN_DIR $f
            if (Test-Path $p) { $Manifest.files[$f] = (Get-FileHash $p -Algorithm SHA256).Hash }
        }
        $Manifest | ConvertTo-Json | Out-File (Join-Path $RUN_DIR "hash_manifest.json") -Encoding utf8
        
        return (Get-FileHash (Join-Path $RUN_DIR "hash_manifest.json") -Algorithm SHA256).Hash
    } catch {
        Write-Host "### [CRITICAL_FAIL] $RunName" -ForegroundColor Red
        return $null
    }
}

# --- 2회 연속 실행 및 비교 ---
$Hash1 = Run-Sealed-Process "RUN_001"
$Hash2 = Run-Sealed-Process "RUN_002"

Write-Host "`n### [FINAL_AUDIT_REPORT] ###" -ForegroundColor Yellow
Write-Host "RUN_001 Hash: $Hash1"
Write-Host "RUN_002 Hash: $Hash2"

if ($Hash1 -eq $Hash2 -and $Hash1 -ne $null) {
    Write-Host "### [SUCCESS] 2회 연속 봉인 일치. Layer-1 도서관 구축 PASS." -ForegroundColor Green
} else {
    Write-Host "### [FAIL] 봉인 불일치 또는 드리프트 발생. 재확인 필요." -ForegroundColor Red
    exit 2
}

Read-Host "Audit Done. 엔터를 누르면 종료됩니다."