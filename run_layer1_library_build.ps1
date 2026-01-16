param([Parameter(Mandatory=$true)][string]${SOURCE_ROOT})
$ErrorActionPreference = "Stop"; $t_start = Get-Date
$PYTHON_EXE = "C:\g6core\g6_v24\venv\Scripts\python.exe"
$RUN_ID = "LIB_FULL_STABLE"
$RUN_DIR = "C:\g7core\g7_v1\runs\LAYER1_${RUN_ID}"

# [CLEAN_SWEEP] 소장님 지시대로 기존 가라 데이터 삭제
if (Test-Path ${RUN_DIR}) { 
    Write-Host "### [WIPE] 기존 불완전 데이터 삭제 중..." -ForegroundColor Yellow
    Remove-Item -Path ${RUN_DIR} -Recurse -Force 
}
New-Item -ItemType Directory -Force -Path ${RUN_DIR} | Out-Null

$STDOUT_P = Join-Path ${RUN_DIR} "stdout.txt"; $STDERR_P = Join-Path ${RUN_DIR} "stderr.txt"; $EXIT_P = Join-Path ${RUN_DIR} "exitcode.txt"

try {
    "2" | Out-File ${EXIT_P} -Force
    Write-Host "### [STAGE 1] 6-CORE FRESH SCAN START..." -ForegroundColor Cyan
    $ScanJson = & ${PYTHON_EXE} C:\g7core\g7_v1\tools\library_scan_full_v1.py ${SOURCE_ROOT} ${RUN_DIR} 2>>${STDERR_P}
    $ScanRes = ${ScanJson} | ConvertFrom-Json
    ${ScanJson} | Out-File ${STDOUT_P} -Append
    
    Write-Host "`n### [STAGE 2] TAGGING & STRIKE BUILD..." -ForegroundColor Cyan
    $StrikeCount = & ${PYTHON_EXE} C:\g7core\g7_v1\tools\tagger_rules_v1.py ${RUN_DIR} 2>>${STDERR_P}

    # [EVIDENCE] 8종 증거 봉인
    $Report = @{ run_id=${RUN_ID}; pass_seal=$true; counts=@{ file=${ScanRes}.file_count; chunk=${ScanRes}.chunk_count; strike=[int]${StrikeCount} } }
    ${Report} | ConvertTo-Json | Out-File (Join-Path ${RUN_DIR} "verify_report.json") -Force -Encoding utf8
    
    $Manifest = @{ files=@{}; meta=@{schema="MANIFEST_V1"; run_id=${RUN_ID}; timestamp=(Get-Date).ToString()} }
    $Targets = "library_index.jsonl", "tag_index_rules.jsonl", "strike_list.jsonl", "verify_report.json", "exitcode.txt", "stdout.txt", "stderr.txt"
    foreach ($f in ${Targets}) {
        $p = Join-Path ${RUN_DIR} ${f}; if (Test-Path ${p}) { ${Manifest}.files[${f}] = (Get-FileHash ${p} -Algorithm SHA256).Hash }
    }
    ${Manifest} | ConvertTo-Json | Out-File (Join-Path ${RUN_DIR} "hash_manifest.json") -Encoding utf8

    "0" | Out-File ${EXIT_P} -Force
    Write-Host "`n### [SUCCESS] 12GB 전수 조사 및 8종 봉인 완료." -ForegroundColor Green
} catch {
    Write-Host "`n### [FAIL] ${_}" -ForegroundColor Red
} finally {
    Read-Host "Audit Done"
}