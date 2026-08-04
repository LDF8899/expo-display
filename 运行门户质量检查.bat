@echo off
chcp 65001 >nul
setlocal
title Portal Quality Gate

cd /d "%~dp0"

if not exist "scripts\portal_quality_gate.py" (
  echo scripts\portal_quality_gate.py not found.
  pause
  exit /b 1
)

echo Running portal quality gate...
echo This checks syntax, blueprint data, CSP/cache rules, portal APIs, QR boundary, department layout, admin routes, and package integrity.
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 scripts\portal_quality_gate.py
) else (
  python scripts\portal_quality_gate.py
)

if errorlevel 1 (
  echo.
  echo Portal quality gate failed.
  echo Fix the first failed check above, then run this file again.
  pause
  exit /b 1
)

echo.
echo Portal quality gate passed.
pause
