# C:\g7core\g7_v1\tools\RUN_V7_WIZARD.ps1
# 목적: 클릭/선택 기반 실행 + 로그 저장 + 에러나도 창 안 닫힘

$ErrorActionPreference = "Stop"

$ROOT = "C:\g7core\g7_v1"
$TOOLS = Join-Path $ROOT "tools"
$QUEUE = Join-Path $ROOT "queue"
$ORDERS_DIR = Join-Path $QUEUE "work_orders"
$PROMPTS_DIR = Join-Path $QUEUE "prompts"
$RUNS = Join-Path $ROOT "runs"
$LOGDIR = Join-Path $RUNS ("wizard_logs\" + (Get-Date -Format "yyyyMMdd_HHmmss"))
New-Item -ItemType Directory -Force -Path $LOGDIR | Out-Null

function Pause-End($msg) {
  Write-Host ""
  Write-Host $msg
  Read-Host "Press Enter to close..."
}

function Run-Step($title, $cmd) {
  $out = Join-Path $LOGDIR ($title + "_stdout.txt")
  $err = Join-Path $LOGDIR ($title + "_stderr.txt")
  Write-Host ""
  Write-Host "=== $title ==="
  Write-Host "Command: $cmd"
  try {
    # cmd /c를 사용하여 파이썬 실행 보장
    cmd /c "$cmd 1> $out 2> $err"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $title"
    } else {
        throw "ExitCode: $LASTEXITCODE"
    }
  } catch {
    Write-Host "[FAIL] $title"
    Write-Host "See logs at: $LOGDIR"
    Write-Host "Error: $_"
    throw
  }
}

try {
  Write-Host ""
  Write-Host "=== G7X V7 Wizard (One-Key Solution) ==="
  Write-Host "ROOT: $ROOT"
  Write-Host "LOGS: $LOGDIR"
  Write-Host ""

  # STEP A: 현재 주문서 수 확인
  $orderCount = 0
  if (Test-Path $ORDERS_DIR) {
    $orderCount = (Get-ChildItem $ORDERS_DIR -Filter *.json -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
  }
  Write-Host "Current work_orders count: $orderCount"
  Write-Host ""

  # STEP B: python.exe 안전 종료
  $kill = Read-Host "Kill running python processes? (y/n)"
  if ($kill -eq "y") {
    $p = Get-Process -Name python -ErrorAction SilentlyContinue
    if ($null -ne $p) {
      # 에러 무시하고 강제 종료
      taskkill /F /IM python.exe /T 2> $null
      Write-Host "[OK] Python processes killed."
    } else {
      Write-Host "[SKIP] No python.exe found (Clean)."
    }
  }

  # STEP C: 환경정화 (Factory Reset)
  $reset = Read-Host "Run factory_reset_v1.py? (y/n)"
  if ($reset -eq "y") {
    $script = Join-Path $TOOLS "factory_reset_v1.py"
    Run-Step "factory_reset" "python $script"
  }

  # STEP D: 주문서 192 재생성 (여기가 '경로 꼬임' 잡는 핵심)
  $gen = Read-Host "Generate 192 orders + prompts (work_order_generator_v2.py)? (y/n)"
  if ($gen -eq "y") {
    $script = Join-Path $TOOLS "work_order_generator_v2.py"
    Run-Step "order_gen" "python $script"
  }

  # STEP E: 엔진 가동 (V7 Main)
  $run = Read-Host "Run main.py (API Workers=3)? (y/n)"
  if ($run -eq "y") {
    $main = Join-Path $ROOT "main.py"
    Run-Step "main_run" "python $main"
  }

  # STEP F: 검증 + 요약
  $verify = Read-Host "Run verifier + devlog summary? (y/n)"
  if ($verify -eq "y") {
    $v = Join-Path $TOOLS "verifier_v1.py"
    Run-Step "verifier" "python $v"
    $d = Join-Path $TOOLS "devlog_manager.py"
    Run-Step "devlog_summary" "python $d --action SUMMARY"
  }

  Pause-End "DONE. All steps finished. Logs saved under: $LOGDIR"

} catch {
  Pause-End "CRITICAL ERROR. Check logs under: $LOGDIR"
}