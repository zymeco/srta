@echo off
title Stock Real Trader Analyzer

cd /d "%~dp0"

echo ============================================================
echo  Stock Real Trader Analyzer
echo ============================================================
echo.

REM ---- 1] Python / Node check ----
where python >nul 2>&1
if errorlevel 1 goto err_python
echo [OK] Python found.

where node >nul 2>&1
if errorlevel 1 goto err_node
echo [OK] Node.js found.

REM ---- 2] Backend deps ----
python -c "import fastapi" >nul 2>&1
if errorlevel 1 goto install_backend
goto check_frontend_deps

:install_backend
echo [Setup] Installing backend dependencies ... first time only
python -m pip install --quiet -r backend\requirements.txt
if errorlevel 1 goto err_backend
goto check_frontend_deps

:check_frontend_deps
echo [OK] Backend deps ready.
if not exist "frontend\node_modules" goto install_frontend
goto check_dist

:install_frontend
echo [Setup] Installing frontend dependencies ... first time only, 1-2 min
pushd frontend
call npm install --silent
if errorlevel 1 goto err_npm
popd
goto check_dist

:check_dist
echo [OK] Frontend deps ready.
if "%1"=="rebuild" rmdir /s /q frontend\dist 2>nul
if not exist "frontend\dist\index.html" goto build_frontend
goto check_port

:build_frontend
echo [Setup] Building frontend ...
pushd frontend
call npm run build
if errorlevel 1 goto err_build
popd
goto check_port

:check_port
echo [OK] Frontend build ready.
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 goto run_server
echo.
echo [WARN] Port 8000 already in use:
netstat -ano | findstr ":8000" | findstr "LISTENING"
echo.
echo Close the existing server first, then run this again.
echo.
pause
exit /b 1

:run_server
echo.
echo ============================================================
echo  Server starting on port 8000
echo ============================================================
echo.
echo   PC browser : http://localhost:8000
echo.
echo   Phone access on same Wi-Fi - your IPv4 addresses:
echo   -----------------------------------------------
ipconfig | findstr /c:"IPv4"
echo   -----------------------------------------------
echo   On phone Chrome, open  http://[your_IP]:8000
echo   Then menu - "Add to Home screen"  to install as app.
echo.
echo   Press Ctrl+C to stop the server.
echo ============================================================
echo.

REM Open browser after a short delay (errors silently ignored)
start "Open Browser" /MIN cmd /c "ping -n 4 127.0.0.1 >nul & start http://localhost:8000" 2>nul

python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000

echo.
echo ============================================================
echo  Server stopped.
echo ============================================================
pause
exit /b 0

:err_python
echo [ERROR] Python is not installed or not in PATH.
echo         Install Python 3.10+ from https://www.python.org/downloads/
pause
exit /b 1

:err_node
echo [ERROR] Node.js is not installed or not in PATH.
echo         Install Node.js 18+ from https://nodejs.org/
pause
exit /b 1

:err_backend
echo [ERROR] Backend dependency install failed.
echo         Try:  python -m pip install -r backend\requirements.txt
pause
exit /b 1

:err_npm
popd
echo [ERROR] npm install failed.
pause
exit /b 1

:err_build
popd
echo [ERROR] Frontend build failed.
pause
exit /b 1
