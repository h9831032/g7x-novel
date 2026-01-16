param([string]${PacketPath})
$ErrorActionPreference = "Stop"
try {
    if (-not (Test-Path ${PacketPath})) { throw "Packet Not Found: ${PacketPath}" }
    ${Data} = Get-Content ${PacketPath} | Where-Object { $_.Trim() -and -not $_.StartsWith("#") }
    ${Count} = (${Data} | Measure-Object).Count
    if (${Count} -ne 120) { throw "ROWS_MISMATCH: 120 required, got ${Count}" }
    
    ${RealWork} = ${Data} | Where-Object { $_.Split('|')[2].Trim() -match "BUILD|PATCH|WIRE|DATA" }
    ${RealCount} = (${RealWork} | Measure-Object).Count
    if (${RealCount} -lt 90) { throw "PAYLOAD_QUOTA_FAIL: RealWork ${RealCount} is below 90" }
    
    return $true
} catch {
    Write-Host " [FAIL_FAST] ${PSItem}" -ForegroundColor Red
    return $false
}
