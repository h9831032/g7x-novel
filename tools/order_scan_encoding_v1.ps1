# G7X Order Encoding Guard v1
# Scans 5 random GPTORDER files for encoding corruption

$ErrorActionPreference = "Stop"
$SSOT_ROOT = "C:\g7core\g7_v1"
$GPTORDER_DIR = "$SSOT_ROOT\GPTORDER"

Write-Host "[ENCODING_GUARD] Scanning GPTORDER files for corruption..." -ForegroundColor Cyan

# Get all txt files
$allFiles = Get-ChildItem "$GPTORDER_DIR\*.txt" -File | Where-Object { $_.Name -like "REAL*" -or $_.Name -like "GPTORDER_G7X_*" }

if ($allFiles.Count -eq 0) {
    Write-Host "[WARN] No GPTORDER files found" -ForegroundColor Yellow
    exit 0
}

# Select 5 random files (or all if less than 5)
$sampleSize = [Math]::Min(5, $allFiles.Count)
$sampleFiles = $allFiles | Get-Random -Count $sampleSize

Write-Host "[INFO] Scanning $sampleSize files..." -ForegroundColor Gray

$corruptionFound = $false

foreach ($file in $sampleFiles) {
    Write-Host ""
    Write-Host "[FILE] $($file.Name)" -ForegroundColor Yellow

    # Read file content
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $lines = Get-Content $file.FullName -Encoding UTF8

    # Sample lines: first 30, middle 30, last 30
    $totalLines = $lines.Count
    $topLines = $lines | Select-Object -First 30
    $middleStart = [Math]::Max(0, [Math]::Floor($totalLines / 2) - 15)
    $middleLines = $lines | Select-Object -Skip $middleStart -First 30
    $bottomLines = $lines | Select-Object -Last 30

    # Check for corruption markers
    $corruptionMarkers = @("�", "??", "ï¿½")

    Write-Host "  Top 30 lines:" -ForegroundColor Gray
    foreach ($line in $topLines | Select-Object -First 5) {
        Write-Host "    $line" -ForegroundColor DarkGray
    }

    Write-Host "  Middle 30 lines:" -ForegroundColor Gray
    foreach ($line in $middleLines | Select-Object -First 5) {
        Write-Host "    $line" -ForegroundColor DarkGray
    }

    Write-Host "  Bottom 30 lines:" -ForegroundColor Gray
    foreach ($line in $bottomLines | Select-Object -First 5) {
        Write-Host "    $line" -ForegroundColor DarkGray
    }

    # Detect corruption
    foreach ($marker in $corruptionMarkers) {
        if ($content -like "*$marker*") {
            Write-Host "  [CORRUPTION DETECTED] Found marker: $marker" -ForegroundColor Red
            $corruptionFound = $true
        }
    }

    # Check for non-ASCII characters (excluding Korean)
    $nonAsciiCount = 0
    foreach ($char in $content.ToCharArray()) {
        $charCode = [int]$char
        # Allow ASCII (0-127) and Korean range (0xAC00-0xD7A3)
        if ($charCode -gt 127 -and -not ($charCode -ge 0xAC00 -and $charCode -le 0xD7A3)) {
            $nonAsciiCount++
        }
    }

    if ($nonAsciiCount -gt 0) {
        Write-Host "  [INFO] Non-ASCII characters found: $nonAsciiCount" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Encoding Guard Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Files scanned: $sampleSize" -ForegroundColor Gray
Write-Host "Corruption found: $(if ($corruptionFound) { 'YES' } else { 'NO' })" -ForegroundColor $(if ($corruptionFound) { "Red" } else { "Green" })
Write-Host "========================================" -ForegroundColor Cyan

if ($corruptionFound) {
    Write-Host "[FAIL] Encoding corruption detected!" -ForegroundColor Red
    exit 1
} else {
    Write-Host "[PASS] No encoding corruption detected" -ForegroundColor Green
    exit 0
}
