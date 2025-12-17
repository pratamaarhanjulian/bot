@echo off
echo ========================================
echo   AUREA PRIME ELITE - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.9 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/6] Python detected
echo.

REM Create virtual environment
if not exist "venv" (
    echo [2/6] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo [2/6] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

REM Upgrade pip
echo [4/6] Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo [5/6] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Setup database
echo [6/6] Setting up database...
if not exist "database" mkdir database
python -c "from database.setup_db import setup_database; setup_database()"
if %errorlevel% neq 0 (
    echo [WARNING] Database setup failed - will retry on first run
)
echo.

REM Run configuration setup
if not exist "config.py" (
    echo ========================================
    echo   Configuration Setup Required
    echo ========================================
    echo.
    python setup_config.py
    if %errorlevel% neq 0 (
        echo [ERROR] Configuration setup failed
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo To start the bot, run: start.bat
echo.
pause
