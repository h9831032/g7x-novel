@echo off
setlocal enabledelayedexpansion
set "ROOT=C:\g7core\g7_v1"

echo ==================================================
echo [G7X] EMERGENCY SYSTEM IGNITION START
echo ==================================================

:: 1. 진짜 파이썬 경로 강제 탐색
echo >>> Finding Real Python Path...
for /f "delims=" %%i in ('where python') do (
    set "REAL_PY=%%i"
    if not "!REAL_PY!"=="!REAL_PY:WindowsApps=!" (
        echo Skipping Windows Store Fake...
    ) else (
        goto :FOUND
    )
)

:FOUND
if "!REAL_PY!"=="" (
    echo !!! [FAIL] Real Python NOT FOUND. 
    echo Please install Python from python.org.
    pause
    exit /b
)
echo >>> Real Python Found: !REAL_PY!

:: 2. 엔진 실행 (팝업 절대 방지)
echo >>> Launching Total Engine v3.2...
"!REAL_PY!" -u "%ROOT%\total_ignition.py"

if %ERRORLEVEL% neq 0 (
    echo !!! [CRITICAL] Engine Crash. Check console.
)

pause