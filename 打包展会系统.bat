@echo off
chcp 65001 >nul
setlocal
title Expo Display Packager

cd /d "%~dp0"

set PACKAGE_NAME=expo-display-deploy.zip
set PACKAGE_PATH=%~dp0..\%PACKAGE_NAME%

echo Packaging expo-display...
echo Output: %PACKAGE_PATH%
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 package_expo.py
) else (
  python package_expo.py
)

if errorlevel 1 (
  echo.
  echo Package failed.
  pause
  exit /b 1
)

echo.
echo Package completed:
echo %PACKAGE_PATH%
pause
