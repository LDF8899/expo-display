@echo off
chcp 65001 >nul
setlocal
title Expo Display Packager

cd /d "%~dp0"

set "PACKAGE_NAME=expo-display-deploy.zip"
for %%I in ("%~dp0..\expo-display-deploy.zip") do set "PACKAGE_PATH=%%~fI"

echo Before formal delivery, run:
echo   portal quality gate batch first
echo and confirm:
echo   portal_quality_gate_ok=true
echo.
echo Packaging expo-display...
echo Output: %PACKAGE_PATH%
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  set "PYTHON_CMD=py -3"
) else (
  set "PYTHON_CMD=python"
)

%PYTHON_CMD% package_expo.py

if errorlevel 1 (
  echo.
  echo Package failed.
  pause
  exit /b 1
)

echo.
echo Verifying package integrity...
%PYTHON_CMD% scripts\package_integrity_test.py

if errorlevel 1 (
  echo.
  echo Package integrity check failed.
  echo Fix the issue above, then run this file again.
  pause
  exit /b 1
)

echo.
echo Package completed:
echo %PACKAGE_PATH%
pause
