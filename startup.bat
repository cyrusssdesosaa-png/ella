@echo off
cd /d "%~dp0"
where python >nul 2>&1
if errorlevel 1 (
  echo Python was not found.
  pause
  exit /b 1
)
:loop
python server.py
if %ERRORLEVEL%==0 goto end
if %ERRORLEVEL%==3 (
  echo Ella is already running or port 8765 is busy. Not restarting.
  pause
  goto end
)
echo Server stopped. Starting again in 3 seconds.
timeout /t 3 >nul
goto loop
:end
