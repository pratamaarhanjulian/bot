@echo off
echo ========================================
echo   AUREA PRIME ELITE - Starting...
echo ========================================
echo.

REM Check if config exists
if not exist "config.py" (
    echo [ERROR] config.py not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

REM Start the bot
echo Starting Telegram Bot...
python bot/telegram_bot.py

pause
