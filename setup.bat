@echo off
REM ============================================================
REM  MediFlow AI — Setup Script
REM  Creates two virtual environments and installs dependencies
REM  Run this ONCE from the mediflow-ai folder
REM ============================================================

echo.
echo  ██╗   ███╗   ███╗███████╗██████╗ ██╗███████╗██╗      ██████╗ ██╗    █████╗ ██╗
echo  ██║   ████╗ ████║██╔════╝██╔══██╗██║██╔════╝██║     ██╔═══██╗██║   ██╔══██╗██║
echo  ██║   ██╔████╔██║█████╗  ██║  ██║██║█████╗  ██║     ██║   ██║██║   ███████║██║
echo  ██║   ██║╚██╔╝██║██╔══╝  ██║  ██║██║██╔══╝  ██║     ██║   ██║██║   ██╔══██║██║
echo  ╚════╝██║ ╚═╝ ██║███████╗██████╔╝██║██║     ███████╗╚██████╔╝███████╗  ██║██║
echo         ╚═╝     ╚═╝╚══════╝╚═════╝ ╚═╝╚═╝     ╚══════╝ ╚═════╝ ╚══════╝  ╚═╝╚═╝
echo.
echo  MediFlow AI -- Setup Script
echo  ============================================================
echo.

REM ── Check Python ──────────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+ and add to PATH.
    pause
    exit /b 1
)
echo [OK] Python found.

REM ── BACKEND venv ──────────────────────────────────────────
echo.
echo [1/4] Creating backend virtual environment...
cd backend
if not exist venv (
    python -m venv venv
    echo [OK] Backend venv created.
) else (
    echo [SKIP] Backend venv already exists.
)

echo [2/4] Installing backend dependencies (this may take a few minutes)...
call venv\Scripts\activate.bat
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo [OK] Backend dependencies installed.
call venv\Scripts\deactivate.bat
cd ..

REM ── FRONTEND venv ─────────────────────────────────────────
echo.
echo [3/4] Creating frontend virtual environment...
cd frontend
if not exist venv (
    python -m venv venv
    echo [OK] Frontend venv created.
) else (
    echo [SKIP] Frontend venv already exists.
)

echo [4/4] Installing frontend dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo [OK] Frontend dependencies installed.
call venv\Scripts\deactivate.bat
cd ..

echo.
echo  ============================================================
echo  [DONE] Setup complete!
echo.
echo  To start MediFlow AI, run:   run.bat
echo  ============================================================
echo.
pause
