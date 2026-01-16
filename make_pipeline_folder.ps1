# make_pipeline_folder.ps1
$ROOT = "C:\g7core\g7_v1"
$DIR  = Join-Path $ROOT "main\pipeline"

# 1) 폴더 만들기(없으면 생성)
New-Item -ItemType Directory -Force -Path $DIR | Out-Null

# 2) 파일 4개 만들기(없으면 생성, 있으면 유지)
$files = @("catalog.py","evidence.py","runner.py","devlog.py")
foreach ($f in $files) {
  $p = Join-Path $DIR $f
  if (!(Test-Path $p)) {
    New-Item -ItemType File -Force -Path $p | Out-Null
  }
}

Write-Host "OK:"
Write-Host (Join-Path $DIR "catalog.py")
Write-Host (Join-Path $DIR "evidence.py")
Write-Host (Join-Path $DIR "runner.py")
Write-Host (Join-Path $DIR "devlog.py")
