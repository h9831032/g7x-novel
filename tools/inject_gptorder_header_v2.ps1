$headerPath = "C:\g7core\g7_v1\ssot\GPTORDER_HEADER.txt"
$ordersPath = "C:\g7core\g7_v1\GPTORDER"
$marker = "[SSOT MANDATE]"

if (!(Test-Path $headerPath)) { throw "MISSING HEADER FILE: $headerPath" }
if (!(Test-Path $ordersPath)) { throw "MISSING ORDER DIR: $ordersPath" }

$header = [System.IO.File]::ReadAllText($headerPath, [System.Text.Encoding]::UTF8)

function Read-TextSmart($path) {
    $bytes = [System.IO.File]::ReadAllBytes($path)

    # UTF-8 BOM
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        return @{ Text = [System.Text.Encoding]::UTF8.GetString($bytes); Enc = "UTF8_BOM" }
    }

    # Try UTF-8 (no BOM)
    try {
        $t = [System.Text.Encoding]::UTF8.GetString($bytes)
        if ($t -match $marker -or $t -match "[\uAC00-\uD7A3]") {
            return @{ Text = $t; Enc = "UTF8" }
        }
    } catch {}

    # Fallback: CP949 (Korean ANSI)
    $cp949 = [System.Text.Encoding]::GetEncoding(949)
    return @{ Text = $cp949.GetString($bytes); Enc = "CP949" }
}

function Write-TextSmart($path, $text, $encTag) {
    if ($encTag -eq "UTF8_BOM") {
        [System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding($true)))
    } elseif ($encTag -eq "UTF8") {
        [System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding($false)))
    } else {
        $cp949 = [System.Text.Encoding]::GetEncoding(949)
        [System.IO.File]::WriteAllText($path, $text, $cp949)
    }
}

Get-ChildItem $ordersPath -Filter *.txt | ForEach-Object {
    $p = $_.FullName
    $r = Read-TextSmart $p
    $content = $r.Text

    if ($content -notmatch [regex]::Escape($marker)) {
        $newContent = $header + "`r`n`r`n" + $content
        Write-TextSmart $p $newContent $r.Enc
        Write-Host "HEADER INSERTED (enc=$($r.Enc)):" $_.Name
    } else {
        Write-Host "OK (already injected):" $_.Name
    }
}
