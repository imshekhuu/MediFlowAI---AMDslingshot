@echo off
REM ============================================================
REM  MediFlow AI — Quick Start & Test Script
REM  Starts both servers and runs endpoint tests
REM ============================================================

echo.
echo  ============================================================
echo   MediFlow AI - Quick Start
echo  ============================================================
echo.

REM ── Check if setup was run ────────────────────────────────
if not exist backend\venv (
    echo [ERROR] Backend venv not found!
    echo Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

if not exist frontend\venv (
    echo [ERROR] Frontend venv not found!
    echo Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

REM ── Start Backend in background ───────────────────────────
echo [1/3] Starting FastAPI Backend (port 8000)...
cd backend
start /B "MediFlow Backend" cmd /c "call venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1"
cd ..

REM ── Wait for backend to start ─────────────────────────────
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM ── Start Frontend in background ──────────────────────────
echo [2/3] Starting Flask Frontend (port 5000)...
cd frontend
start /B "MediFlow Frontend" cmd /c "call venv\Scripts\activate.bat && python server.py > frontend.log 2>&1"
cd ..

REM ── Wait for frontend to start ────────────────────────────
echo Waiting for frontend to initialize...
timeout /t 3 /nobreak >nul

REM ── Run endpoint tests ────────────────────────────────────
echo.
echo [3/3] Running endpoint connectivity tests...
echo.
python test_endpoints.py

echo.
echo  ============================================================
echo   MediFlow AI is running!
echo  ============================================================
echo   Frontend:  http://localhost:5000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo  ============================================================
echo.
echo   Press any key to open the application in your browser...
pause >nul

start http://localhost:5000

echo.
echo   Servers are running in the background.
echo   Check backend.log and frontend.log for server output.
echo   To stop servers, close this window or run: taskkill /IM python.exe /F
echo.
pause
