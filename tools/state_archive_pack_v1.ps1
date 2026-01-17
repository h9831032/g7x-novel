# G7X State Archive Pack v1
# Creates timestamped archive of critical project files

$ErrorActionPreference = "Stop"
$SSOT_ROOT = "C:\g7core\g7_v1"
$DEVLOG_DIR = "$SSOT_ROOT\DEVLOG"

# Create timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$archive_name = "STATE_ARCHIVE_$timestamp"
$archive_dir = "$DEVLOG_DIR\$archive_name"
$zip_file = "$DEVLOG_DIR\$archive_name.zip"

Write-Host "[STATE_ARCHIVE] Creating state archive..." -ForegroundColor Cyan

# Create archive directory
New-Item -ItemType Directory -Path $archive_dir -Force | Out-Null

# Copy critical files
Write-Host "[COPY] Copying manager.py..." -ForegroundColor Gray
Copy-Item "$SSOT_ROOT\main\manager.py" "$archive_dir\" -ErrorAction SilentlyContinue

Write-Host "[COPY] Copying GPTORDER files..." -ForegroundColor Gray
New-Item -ItemType Directory -Path "$archive_dir\GPTORDER" -Force | Out-Null
Copy-Item "$SSOT_ROOT\GPTORDER\*.txt" "$archive_dir\GPTORDER\" -ErrorAction SilentlyContinue

Write-Host "[COPY] Copying DEVLOG files..." -ForegroundColor Gray
New-Item -ItemType Directory -Path "$archive_dir\DEVLOG" -Force | Out-Null
Copy-Item "$SSOT_ROOT\DEVLOG\*.md" "$archive_dir\DEVLOG\" -ErrorAction SilentlyContinue
Copy-Item "$SSOT_ROOT\DEVLOG\*.jsonl" "$archive_dir\DEVLOG\" -ErrorAction SilentlyContinue
Copy-Item "$SSOT_ROOT\DEVLOG\*.json" "$archive_dir\DEVLOG\" -ErrorAction SilentlyContinue

Write-Host "[COPY] Copying DOCS files..." -ForegroundColor Gray
New-Item -ItemType Directory -Path "$archive_dir\DOCS" -Force | Out-Null
Copy-Item "$SSOT_ROOT\DOCS\*.md" "$archive_dir\DOCS\" -ErrorAction SilentlyContinue

# Create manifest
$manifest = @"
G7X State Archive
Created: $timestamp
Location: $archive_dir

Contents:
- main/manager.py
- GPTORDER/*.txt
- DEVLOG/*.md, *.jsonl, *.json
- DOCS/*.md
"@

$manifest | Out-File "$archive_dir\MANIFEST.txt" -Encoding UTF8

# Compress to ZIP
Write-Host "[ZIP] Compressing archive..." -ForegroundColor Yellow
Compress-Archive -Path $archive_dir -DestinationPath $zip_file -Force

# Cleanup temp directory
Remove-Item $archive_dir -Recurse -Force

Write-Host ""
Write-Host "[SUCCESS] State archive created!" -ForegroundColor Green
Write-Host "  ZIP: $zip_file" -ForegroundColor Gray
Write-Host ""

Write-Host "ARCHIVE_PATH: $zip_file"
exit 0
