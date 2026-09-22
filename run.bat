@echo off
REM Schedule King - one command to set up and run everything (Windows).
REM   run.bat               set up (first time only) and launch the app
REM   run.bat --sample      launch with the bundled sample catalog loaded
REM   run.bat test          run the full test suite
setlocal
set "ROOT=%~dp0"
set "APP_DIR=%ROOT%Schedule-King"
set "VENV=%APP_DIR%\.venv"
set "PY=%VENV%\Scripts\python.exe"

if not exist "%PY%" (
    echo Creating virtual environment...
    py -3 -m venv "%VENV%" 2>nul || python -m venv "%VENV%" || (echo Python 3.8+ is required: https://www.python.org/downloads/ & exit /b 1)
    "%PY%" -m pip install --quiet --upgrade pip
    echo Installing dependencies ^(first run only^)...
    "%PY%" -m pip install --quiet -r "%APP_DIR%\requirements.txt" || exit /b 1
)

cd /d "%APP_DIR%"
if /i "%~1"=="test" (
    set QT_QPA_PLATFORM=offscreen
    "%PY%" -m pytest -q -p no:cacheprovider
    exit /b %errorlevel%
)
"%PY%" main.py %*
