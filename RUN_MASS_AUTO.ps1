$ErrorActionPreference="Stop"
$K="AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
$U="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=$K"
$P="C:\g6core\g6_v24\data\umr\chunks"
$R="C:\g7core\g7_v1\runs\RUN_MASS_$(Get-Date -f HHmmss)"
$D="$R\payload"
New-Item -ItemType Directory -Path $D -Force | Out-Null
$Fs=Get-ChildItem $P -File
Write-Host ">>> [MASS_START] Total: $($Fs.Count)" -F Yellow
foreach($F in $Fs){try{$T=Get-Content $F.FullName -Raw -Encoding UTF8;$TS=$T.Substring(0,[Math]::Min($T.Length,1500));$B=@{contents=@(@{parts=@(@{text="Analyze this novel for errors (JSON): $TS"})})} | ConvertTo-Json -Depth 5;$Rs=Invoke-RestMethod -Uri $U -Method Post -Body $B -ContentType "application/json";$Res=$Rs.candidates[0].content.parts[0].text;$Clean=$Res -replace "```json","" -replace "```","";$SP="$D\row_$($F.Name).json";$Clean | Out-File $SP -Encoding UTF8;Write-Host " [OK] $($F.Name)" -F Green}catch{Write-Host " [FAIL] $($F.Name): $_" -F Red}};Read-Host "Audit Done"
