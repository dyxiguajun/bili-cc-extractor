@echo off
setlocal EnableExtensions

set "APP_DIR=%~dp0..\backend"
set "VENV_DIR=%APP_DIR%\.venv"
set "HOST=127.0.0.1"
set "PORT=8000"
set "URL=http://%HOST%:%PORT%/"

echo.
echo Starting Bili CC Extractor Tools...

echo.
echo [1/6] Enter backend folder...
cd /d "%APP_DIR%" || (
  echo [ERROR] backend folder not found: %APP_DIR%
  pause
  exit /b 1
)

echo.
echo [2/6] Check port %PORT%...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
  echo [INFO] Port %PORT% is already in use. PID=%%p
  echo        The app may already be running.
  start "" "%URL%"
  exit /b 0
)

echo.
echo [3/6] Ensure venv...
if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo Creating venv at %VENV_DIR% ...
  py -3.12 -m venv "%VENV_DIR%" 2>nul
  if errorlevel 1 (
    python -m venv "%VENV_DIR%"
  )
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo [ERROR] venv creation failed.
  pause
  exit /b 1
)

echo.
echo [4/6] Activate venv...
call "%VENV_DIR%\Scripts\activate.bat"

echo.
echo [5/6] Install requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo [6/6] Open browser and run server...
start "" "%URL%"
python -m uvicorn app:app --reload --host %HOST% --port %PORT%

endlocal
