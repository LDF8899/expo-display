@echo off
chcp 65001 >nul
setlocal
title Expo Display System

cd /d "%~dp0"

if not exist "start_expo.py" (
  echo start_expo.py not found.
  pause
  exit /b 1
)

set OPEN_BROWSER=1
set OPEN_ADMIN=0
set START_SCANNER_AGENT=1

echo Starting expo display system...
echo Display page will open automatically.
echo Keep this window open during the exhibition.
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 start_expo.py --kill-existing
) else (
  python start_expo.py --kill-existing
)

echo.
echo Expo display system stopped.
pause
