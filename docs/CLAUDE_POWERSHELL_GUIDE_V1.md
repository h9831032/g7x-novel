# Claude Code PowerShell Compatibility Guide V1

## Overview
This guide documents how to use Claude Code CLI with PowerShell scripts in the G7X project, including auto-detection patterns and safe execution practices.

## Auto-Detection Rules

Claude Code should automatically detect when a command or file is a PowerShell script based on these patterns:

### File Extension Detection
- `.ps1` files are PowerShell scripts
- `.psm1` files are PowerShell modules
- `.psd1` files are PowerShell data files

### Command Detection
When Claude sees commands like:
```
run tools/script.ps1
execute run_real24_skeleton.ps1
./tools/order_scan_encoding_v1.ps1
```

Claude should recognize these as PowerShell scripts and execute them using PowerShell, not bash.

## Safe Execution Pattern

### Windows Environment
When executing `.ps1` files on Windows, use PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File C:\g7core\g7_v1\tools\script.ps1
```

**Why `-ExecutionPolicy Bypass`?**
- G7X scripts are local, trusted automation tools
- Bypassing execution policy prevents "script not digitally signed" errors
- Only applies to the single script execution, not system-wide
- Safe for development and automation workflows

### Cross-Platform Consideration
On Linux/Mac, PowerShell Core (`pwsh`) can be used:
```bash
pwsh -File /path/to/script.ps1
```

However, G7X is primarily a Windows project, so PowerShell 5.1+ is the default.

## Common Errors and Fixes

### Error 1: "File cannot be loaded because running scripts is disabled"
**Cause**: ExecutionPolicy is Restricted
**Fix**: Use `-ExecutionPolicy Bypass` flag

### Error 2: "The term 'script.ps1' is not recognized"
**Cause**: Trying to run `.ps1` as bash command
**Fix**: Explicitly invoke with `powershell -File`

### Error 3: "Permission denied"
**Cause**: File permissions or path issue
**Fix**: Use absolute paths and check file exists

## G7X Script Inventory

### Batch Runners (3+3×N pattern)
- `run_real24_skeleton.ps1` - REAL24 execution with evidence validation
- `run_real24_3p3x4_day_night.ps1` - REAL24 4-batch runner
- `run_real30_3p3x5_day_night.ps1` - REAL30 5-batch runner
- `run_real36_3p3x6_day_night.ps1` - REAL36 6-batch runner

### Validation Tools
- `order_scan_encoding_v1.ps1` - Encoding corruption detector
- `verify_e2e_v1.ps1` - End-to-end verification
- `inject_gptorder_header_v2.ps1` - Header injection tool

### Utility Scripts
- `_resolve_python_path.ps1` - Python venv path resolver
- `state_archive_pack_v1.ps1` - State archiving tool
- `run_real_smoke_pack_v1.ps1` - Smoke test pack runner

## Claude Code Integration

### Recommended Auto-Approval
For trusted G7X scripts in known locations, Claude Code can auto-approve execution without prompting:

**Safe patterns**:
- `tools/*.ps1` (all scripts in tools directory)
- `run_real*.ps1` (batch runners)
- `*_v1.ps1` (versioned tools)

**Require confirmation**:
- Scripts outside `tools/` directory
- Scripts without version suffix
- Scripts with dangerous operations (Remove-Item, Clear-Content, etc.)

### Example Claude Code Session

**User input**:
```
Run the REAL24 skeleton with NIGHT profile
```

**Claude Code should detect**:
1. User wants to run `run_real24_skeleton.ps1`
2. Script is in `tools/` directory
3. Needs parameter: `-Profile NIGHT`
4. Should execute via PowerShell

**Claude Code execution**:
```powershell
powershell -ExecutionPolicy Bypass -File C:\g7core\g7_v1\tools\run_real24_skeleton.ps1 -OrderFile GPTORDER/REAL24.txt -Profile NIGHT
```

## Security Considerations

### Why ExecutionPolicy Bypass is Safe Here
1. **Trusted source**: All scripts are part of G7X project
2. **Version controlled**: Scripts tracked in git, auditable
3. **Local execution**: No remote script execution
4. **Scoped**: Only applies to single command, not system-wide

### Alternative: Sign Scripts
For production use, scripts can be digitally signed:
```powershell
Set-AuthenticodeSignature -FilePath script.ps1 -Certificate $cert
```

But for development, `-ExecutionPolicy Bypass` is standard practice.

## Best Practices

1. **Always use absolute paths** when calling from Python or other scripts
2. **Check exit codes**: All G7X scripts return 0 (success) or 1 (failure)
3. **Capture output**: Use `2>&1` to capture both stdout and stderr
4. **Set ErrorActionPreference**: Scripts use `$ErrorActionPreference = "Stop"` for fail-fast behavior
5. **Validate parameters**: Scripts validate required parameters and show usage on error

## Testing Script Detection

To test if Claude Code correctly detects PowerShell:

**Test 1**: Extension detection
```
claude: run tools/order_scan_encoding_v1.ps1
# Should execute via PowerShell
```

**Test 2**: Parameter passing
```
claude: run run_real24_skeleton.ps1 with profile NIGHT
# Should detect -Profile parameter and pass correctly
```

**Test 3**: Path resolution
```
claude: execute the encoding scanner
# Should resolve to tools/order_scan_encoding_v1.ps1 and run via PowerShell
```

## Troubleshooting

### Claude executes .ps1 as bash
**Symptom**: Syntax errors like "unexpected token"
**Fix**: Update Claude's file type detection rules to include `.ps1` → PowerShell

### Parameters not passed correctly
**Symptom**: Script shows usage help instead of running
**Fix**: Ensure Claude passes parameters in PowerShell syntax (`-Param Value`)

### Script not found
**Symptom**: "File not found" or "path does not exist"
**Fix**: Use absolute paths or ensure working directory is G7X root

## Version History

- **V1** (2026-01-17): Initial PowerShell compatibility guide
  - Auto-detection rules documented
  - Safe execution pattern established
  - Script inventory compiled
  - Security considerations explained

---

**Document ID**: CLAUDE_POWERSHELL_GUIDE_V1
**Created**: 2026-01-17
**Status**: ACTIVE
