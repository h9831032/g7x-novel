$headerPath = "C:\g7core\g7_v1\ssot\GPTORDER_HEADER.txt"
$ordersPath = "C:\g7core\g7_v1\GPTORDER"
if (!(Test-Path $headerPath)) { throw "MISSING HEADER FILE: $headerPath" }

$header = Get-Content $headerPath -Raw

Get-ChildItem $ordersPath -Filter *.txt | ForEach-Object {
    $content = Get-Content $_.FullName -Raw

    if ($content -notmatch "\[SSOT MANDATE\]") {
        $newContent = $header + "`r`n`r`n" + $content
        Set-Content $_.FullName $newContent -Encoding UTF8
        Write-Host "HEADER INSERTED:" $_.Name
    } else {
        Write-Host "OK (already injected):" $_.Name
    }
}
