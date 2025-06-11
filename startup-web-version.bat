@echo off
echo ========================================
echo Clip Marker Web Version Startup
echo ========================================

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤：未找到 Node.js，請先安裝 Node.js
    echo 下載地址：https://nodejs.org/
    pause
    exit /b 1
)

:: Check if npm dependencies are installed
if not exist node_modules (
    echo 正在安裝 Electron 依賴套件...
    npm install
    if errorlevel 1 (
        echo 錯誤：無法安裝 Electron 依賴套件
        pause
        exit /b 1
    )
)

:: Check if frontend dependencies are installed
if not exist frontend\node_modules (
    echo 正在安裝前端依賴套件...
    cd frontend
    npm install
    if errorlevel 1 (
        echo 錯誤：無法安裝前端依賴套件
        pause
        exit /b 1
    )
    cd ..
)

:: Check if Python virtual environment exists
if not exist backend\venv (
    echo 虛擬環境不存在，請先執行 setup-flask.bat
    echo 正在自動執行設定...
    call setup-flask.bat
    if errorlevel 1 (
        echo 錯誤：Flask 後端設定失敗
        pause
        exit /b 1
    )
)

:: Set environment variables
set NODE_ENV=development
set NUXT_IS_ELECTRON=true

echo.
echo 正在啟動服務...
echo.

:: Start Flask backend in background
echo 啟動 Flask 後端 (http://localhost:5000)...
start /B cmd /c "cd backend && venv\Scripts\activate && python app.py"

:: Wait a moment for Flask to start
timeout /t 3 /nobreak >nul

:: Start Nuxt frontend in background
echo 啟動 Nuxt3 前端 (http://localhost:3000)...
start /B cmd /c "cd frontend && npm run dev"

:: Wait for services to start
echo 等待服務啟動...
timeout /t 5 /nobreak >nul

:: Start Electron
echo 啟動 Electron 應用程式...
npm run dev:electron

echo.
echo 應用程式已關閉
pause 