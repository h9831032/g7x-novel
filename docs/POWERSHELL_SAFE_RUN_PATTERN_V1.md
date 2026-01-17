# PowerShell Safe Run Pattern V1

## Overview
This document establishes the mandatory safe execution pattern for all PowerShell scripts in the G7X project to ensure consistent error handling, exit codes, and evidence generation.

## The Safe Run Pattern

Every PowerShell script in G7X must follow this template:

```powershell
# Script Name and Purpose
# Version: v1
# Description: [What this script does]

param(
    [Parameter(Mandatory=$false)]
    [string]$RequiredParam,

    [Parameter(Mandatory=$false)]
    [ValidateSet("Option1", "Option2")]
    [string]$OptionalParam = "Option1"
)

$ErrorActionPreference = "Stop"  # MANDATORY: Fail-fast on errors
$SSOT_ROOT = "C:\g7core\g7_v1"   # MANDATORY: Fixed root path

# Validation block
if (-not $RequiredParam) {
    Write-Host "[FAIL] RequiredParam is mandatory" -ForegroundColor Red
    Write-Host "Usage: script.ps1 -RequiredParam <value>" -ForegroundColor Yellow
    exit 1
}

# Dependency checks
if (-not (Test-Path $SSOT_ROOT)) {
    Write-Host "[FAIL] SSOT_ROOT not found: $SSOT_ROOT" -ForegroundColor Red
    exit 1
}

# Header (optional, for visibility)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Script Name v1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Main logic with try-catch
try {
    # Step 1: Description
    Write-Host "[STEP 1/N] Doing thing..." -ForegroundColor Yellow
    # ... work ...
    Write-Host "[PASS] Thing completed" -ForegroundColor Green

    # Step 2: Description
    Write-Host "[STEP 2/N] Doing other thing..." -ForegroundColor Yellow
    # ... work ...
    Write-Host "[PASS] Other thing completed" -ForegroundColor Green

    # Success exit
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SCRIPT COMPLETED SUCCESSFULLY" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    exit 0

} catch {
    # Error handling
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "SCRIPT FAILED" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Line: $($_.InvocationInfo.ScriptLineNumber)" -ForegroundColor Red
    exit 1
}
```

## Mandatory Components

### 1. ErrorActionPreference = "Stop"
**Why**: Ensures script fails immediately on any error, preventing silent failures.

**Example**:
```powershell
$ErrorActionPreference = "Stop"  # FAIL-FAST behavior
```

Without this, PowerShell continues after errors, leading to cascading failures.

### 2. Fixed SSOT_ROOT
**Why**: Ensures scripts work regardless of current directory.

**Example**:
```powershell
$SSOT_ROOT = "C:\g7core\g7_v1"  # Never use relative paths
```

### 3. Parameter Validation
**Why**: Fail early with clear error messages.

**Example**:
```powershell
param(
    [Parameter(Mandatory=$true)]
    [ValidateNotNullOrEmpty()]
    [string]$OrderFile,

    [Parameter(Mandatory=$false)]
    [ValidateSet("DAY", "NIGHT")]
    [string]$Profile = "DAY"
)

# Additional validation
if (-not (Test-Path $OrderFile)) {
    Write-Host "[FAIL] Order file not found: $OrderFile" -ForegroundColor Red
    exit 1
}
```

### 4. Dependency Checks
**Why**: Verify required files/tools exist before proceeding.

**Example**:
```powershell
$PYTHON = "$SSOT_ROOT\.venv\Scripts\python.exe"

if (-not (Test-Path $PYTHON)) {
    Write-Host "[FAIL] Python not found: $PYTHON" -ForegroundColor Red
    exit 1
}
```

### 5. Exit Code Enforcement
**Why**: Scripts must return 0 (success) or 1 (failure) for automation.

**Rules**:
- **0**: Script completed successfully, all validations passed
- **1**: Script failed (error, validation failure, or unexpected state)

**Example**:
```powershell
# Success path
exit 0

# Failure path
Write-Host "[FAIL] Validation failed" -ForegroundColor Red
exit 1
```

### 6. Try-Catch for Critical Sections
**Why**: Graceful error handling with clear messages.

**Example**:
```powershell
try {
    $result = & $PYTHON script.py
    if ($LASTEXITCODE -ne 0) {
        throw "Script returned exit code $LASTEXITCODE"
    }
} catch {
    Write-Host "[FAIL] Execution failed: $_" -ForegroundColor Red
    exit 1
}
```

### 7. Step Markers
**Why**: Progress visibility for long-running scripts.

**Example**:
```powershell
Write-Host "[STEP 1/5] Validating order file..." -ForegroundColor Yellow
# ... work ...
Write-Host "[PASS] Order file valid" -ForegroundColor Green

Write-Host "[STEP 2/5] Executing manager..." -ForegroundColor Yellow
# ... work ...
Write-Host "[PASS] Manager completed" -ForegroundColor Green
```

## Color Coding Standard

Use consistent colors for visibility:

- **Cyan**: Headers, section dividers
- **Yellow**: Step announcements, info messages
- **Green**: Success messages, PASS indicators
- **Red**: Error messages, FAIL indicators
- **Gray**: Supplementary info, debugging output

**Example**:
```powershell
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "G7X Script v1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[STEP 1/3] Processing..." -ForegroundColor Yellow
Write-Host "  Details: xyz" -ForegroundColor Gray
Write-Host "[PASS] Step completed" -ForegroundColor Green
```

## Output Capture Pattern

When calling external programs, capture output correctly:

```powershell
# Capture both stdout and stderr
$output = & $PYTHON script.py 2>&1
$exitCode = $LASTEXITCODE

# Display output
Write-Host $output

# Check exit code
if ($exitCode -ne 0) {
    Write-Host "[FAIL] Script returned exit code $exitCode" -ForegroundColor Red
    exit 1
}
```

## RUN_PATH Extraction Pattern

For scripts that call manager.py, extract RUN_PATH:

```powershell
$output = & $PYTHON "$SSOT_ROOT\main\manager.py" $OrderFile 2>&1
$exitCode = $LASTEXITCODE

Write-Host $output

# Extract RUN_PATH from output
$runPath = $null
foreach ($line in $output -split "`n") {
    if ($line -match "TARGET_RUN_PATH:(.+)") {
        $runPath = $matches[1].Trim()
        break
    }
}

if (-not $runPath) {
    Write-Host "[FAIL] Could not extract RUN_PATH" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] RUN_PATH: $runPath" -ForegroundColor Cyan
```

## Evidence Generation

Scripts that perform critical operations must generate evidence:

```powershell
# Create evidence file
$evidenceFile = "$SSOT_ROOT\STATE_PACK\script_evidence_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

@"
Script: $($MyInvocation.MyCommand.Name)
Timestamp: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Parameters: $($PSBoundParameters | ConvertTo-Json)
Exit Code: 0
Duration: $($duration)s
"@ | Out-File $evidenceFile -Encoding UTF8

Write-Host "[EVIDENCE] Written to: $evidenceFile" -ForegroundColor Gray
```

## Real-World Examples

### Example 1: run_real24_skeleton.ps1
✅ **Follows safe pattern**:
- `$ErrorActionPreference = "Stop"`
- Parameter validation with usage message
- Dependency checks (Python, order file)
- Try-catch for critical sections
- Step markers with color coding
- Exit code enforcement
- RUN_PATH extraction
- Evidence validation via external scripts

### Example 2: order_scan_encoding_v1.ps1
✅ **Follows safe pattern**:
- `$ErrorActionPreference = "Stop"`
- Fixed SSOT_ROOT
- Sample-based validation
- Clear PASS/FAIL verdict
- Exit codes (0 or 1)
- Color-coded output

### Example 3: inject_gptorder_header_v2.ps1
❌ **Needs improvement** (hypothetical):
- Missing `$ErrorActionPreference = "Stop"`
- Uses relative paths
- No try-catch blocks
- Unclear exit code logic

## Enforcement Checklist

Before committing a new PowerShell script:

- [ ] `$ErrorActionPreference = "Stop"` at top
- [ ] Fixed `$SSOT_ROOT` path (no relative paths)
- [ ] Parameter validation with usage message
- [ ] Dependency checks (Test-Path for files/tools)
- [ ] Try-catch for error-prone sections
- [ ] Explicit exit codes (0 or 1)
- [ ] Step markers for visibility
- [ ] Color-coded output (Cyan/Yellow/Green/Red/Gray)
- [ ] RUN_PATH extraction (if calling manager.py)
- [ ] Evidence generation (if modifying state)

## Anti-Patterns to Avoid

### ❌ Silent Continuation
```powershell
# BAD: Errors are ignored
Remove-Item $file -ErrorAction SilentlyContinue
```

### ❌ Relative Paths
```powershell
# BAD: Breaks if run from wrong directory
$file = "..\..\tools\script.ps1"
```

### ❌ No Exit Code
```powershell
# BAD: Script ends without explicit exit
Write-Host "Done"
# Missing: exit 0
```

### ❌ Generic Error Messages
```powershell
# BAD: Unhelpful error message
Write-Host "Error!" -ForegroundColor Red
exit 1
```

### ✅ Correct Alternatives

```powershell
# GOOD: Fail-fast on errors
Remove-Item $file -ErrorAction Stop

# GOOD: Absolute paths
$SSOT_ROOT = "C:\g7core\g7_v1"
$file = "$SSOT_ROOT\tools\script.ps1"

# GOOD: Explicit exit code
Write-Host "[PASS] Script completed successfully" -ForegroundColor Green
exit 0

# GOOD: Descriptive error message
Write-Host "[FAIL] Cannot remove file: $file" -ForegroundColor Red
Write-Host "Reason: File not found or permission denied" -ForegroundColor Red
exit 1
```

## Version History

- **V1** (2026-01-17): Initial safe run pattern documentation
  - Established mandatory components
  - Defined exit code rules
  - Documented color coding standard
  - Provided real-world examples
  - Created enforcement checklist

---

**Document ID**: POWERSHELL_SAFE_RUN_PATTERN_V1
**Created**: 2026-01-17
**Status**: ACTIVE
