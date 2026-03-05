@echo off
REM ========================================
REM  AI Employee - Bronze Tier
REM  Complete Start Script with Auto-Qwen
REM ========================================

echo.
echo ========================================
echo  AI Employee - Bronze Tier
echo  Starting File Watcher + Auto Qwen
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.13+
    pause
    exit /b 1
)

echo.
echo Starting Orchestrator with Auto-Qwen...
echo.
echo This will:
echo   1. Start File System Watcher (monitors Inbox/Drop/)
echo   2. Auto-invoke Qwen Code when files detected
echo   3. Process action files automatically
echo.
echo Press Ctrl+C to stop
echo.

python orchestrator.py --vault "../AI_Employee_Vault" --auto-qwen --verbose

if errorlevel 1 (
    echo.
    echo ERROR: Orchestrator exited with error
    pause
    exit /b 1
)

pause
