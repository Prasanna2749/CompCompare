@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

title CompCompare - Stop Server
echo Stopping CompCompare on port 5000...

set "FOUND=0"
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING"') do (
  set "FOUND=1"
  echo Ending process PID %%P
  taskkill /F /PID %%P >nul 2>&1
)

if "!FOUND!"=="0" (
  echo No CompCompare server was found listening on port 5000.
) else (
  echo Server stopped.
)

echo.
pause
exit /b 0
