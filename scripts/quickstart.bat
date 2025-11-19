@echo off
REM Quick Start Script for RSI Trading Bot (Windows)

echo ==========================================
echo 🚀 RSI Trading Bot - Quick Start
echo ==========================================
echo.

REM Check Python
echo 📌 Checking Python version...
python --version >nul 2>&1 || (
    echo ❌ Python is not installed or not in PATH
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Check .env
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from template...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANT: Please edit .env with your Binance API credentials
    echo    Then run this script again.
    exit /b 1
)

REM Create directories
echo 📁 Creating directories...
if not exist "logs" mkdir logs
if not exist "data\reports" mkdir data\reports

echo.
echo ==========================================
echo ✅ Setup Complete!
echo ==========================================
echo.
echo You can now run the bot with:
echo.
echo   REM Interactive mode (recommended)
echo   python main.py --interactive
echo.
echo   REM Quick start (simulation)
echo   python main.py --symbol ETHUSDT --balance 1000 --simulate
echo.
echo   REM View all options
echo   python main.py --help
echo.
echo 📊 Dashboard: http://localhost:5000
echo.
echo ⚠️  Remember to configure your .env file!
echo.
pause
