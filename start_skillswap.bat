@echo off
title SkillSwap Full-Stack Server
echo ===================================================
echo   Starting SkillSwap (Frontend + Backend Unified)
echo   Accessible at: http://localhost:8000/
echo                  http://127.0.0.1:8000/
echo ===================================================
cd /d "%~dp0skillswap"
set PYTHON_CMD=

where py >nul 2>&1
if not errorlevel 1 set PYTHON_CMD=py -3

if not defined PYTHON_CMD (
    if exist "%LOCALAPPDATA%\Programs\Python\Launcher\py.exe" (
        set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Launcher\py.exe" -3
    )
)

if not defined PYTHON_CMD (
    if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
        set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    )
)

if not defined PYTHON_CMD (
    set PYTHON_CMD=python
)

%PYTHON_CMD% manage.py runserver 0.0.0.0:8000
pause
