@echo off
title AI Kitchen Server
cd /d "%~dp0"
echo =======================================================
echo   🍽️ AI Kitchen Server
echo   Running at: http://127.0.0.1:5000
echo =======================================================
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" app.py
) else (
    python app.py
)
pause
