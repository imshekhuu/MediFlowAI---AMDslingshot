@echo off
REM ============================================================
REM  MediFlow AI — Run Script
REM  Starts FastAPI backend (port 8000) + Flask frontend (port 5000)
REM  Run from the mediflow-ai folder
REM ============================================================

echo.
echo  Starting MediFlow AI Platform...
echo  ============================================================
echo  Backend  (FastAPI)  → http://localhost:8000
echo  Frontend (Flask)    → http://localhost:5000
echo  API Docs            → http://localhost:8000/docs
echo  ============================================================
echo.

REM ── Check venvs exist ──────────────────────────────────────
if not exist backend\venv (
    echo [ERROR] Backend venv not found. Please run setup.bat first.
    pause
    exit /b 1
)
if not exist frontend\venv (
    echo [ERROR] Frontend venv not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM ── Start FastAPI Backend in new window ────────────────────
echo [>>] Starting FastAPI Backend...
start "MediFlow AI - Backend" cmd /k "cd /d "%~dp0backend" && call venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM ── Wait 3 seconds for backend to start ───────────────────
timeout /t 3 /nobreak >nul

REM ── Start Flask Frontend in new window ────────────────────
echo [>>] Starting Flask Frontend...
start "MediFlow AI - Frontend" cmd /k "cd /d "%~dp0frontend" && call venv\Scripts\activate.bat && python server.py"

REM ── Wait then open browser ────────────────────────────────
timeout /t 2 /nobreak >nul
echo.
echo  [>>] Opening browser...
start http://localhost:5000

echo.
echo  ============================================================
echo  MediFlow AI is running!
echo  Close the terminal windows to stop the servers.
echo  ============================================================
echo.
