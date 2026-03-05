@echo off
REM Quick Start Script for AI Employee - Bronze Tier
REM This script starts the File System Watcher

echo ========================================
echo  AI Employee - Bronze Tier
echo  File System Watcher Starting...
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
echo Starting File System Watcher...
echo Watcher will monitor: AI_Employee_Vault\Inbox\Drop\
echo Press Ctrl+C to stop the watcher
echo.

python filesystem_watcher.py --vault "../AI_Employee_Vault" --interval 30

pause
