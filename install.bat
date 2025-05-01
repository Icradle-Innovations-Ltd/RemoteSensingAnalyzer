@echo off
echo Remote Sensing Data Analyzer - Installation Script
echo =================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.9 or newer and try again.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install GDAL using the helper script
echo Installing GDAL...
python install_gdal.py

REM Install other dependencies
echo Installing other dependencies...
pip install -r requirements.txt

echo.
echo Installation completed!
echo.
echo To run the application:
echo 1. Activate the virtual environment: .venv\Scripts\activate
echo 2. Run the application: streamlit run app.py
echo.
pause