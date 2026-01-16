param(
    [string]$DownloadRoot = "$env:USERPROFILE\Downloads"
)

cd C:\g7core\g7_v1

$DL = $DownloadRoot

mkdir tools -ErrorAction SilentlyContinue
Copy-Item "$DL\devlog_writer.py" ".\tools\devlog_writer.py" -Force

Copy-Item ".\manager.py" ".\manager.py.bak_before_v3" -Force
Copy-Item "$DL\manager.py" ".\manager.py" -Force

$PY = "$PWD\.venv\Scripts\python.exe"
& $PY .\manager.py --order_path TEST_DEVLOG_5.txt
