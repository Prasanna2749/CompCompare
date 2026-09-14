@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

title CompCompare Server
echo ========================================
echo   CompCompare - Starting...
echo ========================================
echo.

set "PY_CMD="
set "PY_MODE="

REM 1) Windows Python launcher
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
  if not errorlevel 1 (
    set "PY_MODE=launcher"
    set "PY_CMD=py -3"
  )
)

REM 2) python on PATH
if not defined PY_MODE (
  where python >nul 2>&1
  if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
    if not errorlevel 1 (
      set "PY_MODE=path"
      set "PY_CMD=python"
    )
  )
)

REM 3) Common install folders (works even if PATH was not set)
if not defined PY_MODE (
  for /f "delims=" %%F in ('dir /b /ad /o-n "%LOCALAPPDATA%\Programs\Python\Python3*" 2^>nul') do (
    if not defined PY_MODE if exist "%LOCALAPPDATA%\Programs\Python\%%F\python.exe" (
      "%LOCALAPPDATA%\Programs\Python\%%F\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
      if not errorlevel 1 (
        set "PY_MODE=file"
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\%%F\python.exe"
      )
    )
  )
)

if not defined PY_MODE (
  for /f "delims=" %%F in ('dir /b /ad /o-n "%ProgramFiles%\Python3*" 2^>nul') do (
    if not defined PY_MODE if exist "%ProgramFiles%\%%F\python.exe" (
      "%ProgramFiles%\%%F\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
      if not errorlevel 1 (
        set "PY_MODE=file"
        set "PY_CMD=%ProgramFiles%\%%F\python.exe"
      )
    )
  )
)

if not defined PY_MODE (
  echo ERROR: Python 3.10+ was not found.
  echo.
  echo Install Python from https://www.python.org/downloads/
  echo During setup, enable "Add python.exe to PATH".
  echo.
  pause
  exit /b 1
)

echo Using Python: !PY_CMD!
echo.

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  if /I "!PY_MODE!"=="file" (
    "!PY_CMD!" -m venv .venv
  ) else (
    !PY_CMD! -m venv .venv
  )
  if errorlevel 1 (
    echo ERROR: Could not create .venv
    pause
    exit /b 1
  )
)

set "VENV_PY=%CD%\.venv\Scripts\python.exe"
if not exist "!VENV_PY!" (
  echo ERROR: Virtual environment Python not found.
  pause
  exit /b 1
)

echo Installing / updating dependencies...
"!VENV_PY!" -m pip install --upgrade pip >nul
"!VENV_PY!" -m pip install -r requirements.txt
if errorlevel 1 (
  echo ERROR: Failed to install requirements.
  pause
  exit /b 1
)

echo.
echo Database is created automatically on first start if missing.
echo.
echo Starting Flask server...
echo Open your browser to: http://127.0.0.1:5000
echo.
echo Keep this window open while using the app.
echo Press Ctrl+C to stop, or run stop.bat
echo ========================================
echo.

"!VENV_PY!" app.py
set "EXITCODE=!ERRORLEVEL!"
echo.
echo Server stopped.
pause
exit /b !EXITCODE!
