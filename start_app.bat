@echo off
title ProcessIQ - Starting Application

cd /d "%~dp0"

echo Starting ProcessIQ Backend...
start "ProcessIQ Backend" cmd /k "cd /d "%~dp0backend" && venv\Scripts\activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting ProcessIQ Frontend...
start "ProcessIQ Frontend" cmd /k "cd /d "%~dp0" && npm run dev -- --host 127.0.0.1"

timeout /t 5 /nobreak >nul

echo Opening ProcessIQ...
start http://localhost:5173

echo.
echo ProcessIQ is starting...
echo Frontend: http://localhost:5173
echo Backend:  http://127.0.0.1:8000