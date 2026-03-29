@echo off
REM ========================================
REM  AI Employee - Silver Tier
REM  Start All Watchers (Bronze + Silver)
REM ========================================

echo.
echo ========================================
echo  AI Employee - Silver Tier
echo  Starting All Watchers...
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
echo Starting Orchestrator with Silver Tier watchers...
echo.
echo This will start:
echo   1. File System Watcher (Bronze)
echo   2. Gmail Watcher (Silver)
echo   3. LinkedIn Watcher (Silver)
echo   4. Qwen Code Auto-Processor
echo.
echo Press Ctrl+C to stop
echo.

REM First time Gmail auth may be required
echo NOTE: First time running Gmail Watcher?
echo You will need to authenticate with Google.
echo Follow the URL shown in the logs.
echo.

python orchestrator.py --vault "../AI_Employee_Vault" --silver-tier --auto-qwen --verbose

if errorlevel 1 (
    echo.
    echo ERROR: Orchestrator exited with error
    echo Check logs in AI_Employee_Vault\Logs\
    pause
    exit /b 1
)

pause
