@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo 影片剪輯標記工具 - 快速啟動
echo ========================================

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤：未找到 Node.js，請先安裝 Node.js
    echo 下載地址：https://nodejs.org/
    pause
    exit /b 1
)

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤：未找到 Python，請先安裝 Python
    echo 下載地址：https://www.python.org/
    pause
    exit /b 1
)

echo ✓ Node.js 和 Python 環境檢查完成

:: Auto setup if needed
echo.
echo 檢查專案設定...

:: Install Electron dependencies if needed
if not exist node_modules (
    echo 正在安裝 Electron 依賴套件...
    npm install
    if errorlevel 1 (
        echo 錯誤：無法安裝 Electron 依賴套件
        pause
        exit /b 1
    )
)

:: Setup Flask if needed
if not exist backend\venv (
    echo 正在設定 Flask 後端環境...
    call setup-flask.bat
    if errorlevel 1 (
        echo 錯誤：Flask 後端設定失敗
        pause
        exit /b 1
    )
)

:: Set environment variables
set NODE_ENV=development
set FLASK_ENV=development

:: Install frontend dependencies if needed
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

echo.
echo ========================================
echo 正在啟動服務...
echo ========================================

:: Start Flask backend
echo [1/3] 啟動 Flask 後端服務 (http://localhost:5000)...
start /min cmd /c "title Flask Backend && cd backend && venv\Scripts\activate && python app.py && pause"

:: Wait for Flask to initialize
echo 等待 Flask 後端啟動...
timeout /t 3 /nobreak >nul

:: Start Nuxt3 frontend
echo [2/3] 啟動 Nuxt3 前端服務 (http://localhost:3000)...
start /min cmd /c "title Nuxt3 Frontend && cd frontend && npm run dev && pause"

:: Wait for services to start
echo 等待前端服務啟動...
timeout /t 5 /nobreak >nul

:: Check if services are running
echo 檢查服務狀態...
powershell -command "try { Invoke-WebRequest -Uri 'http://localhost:5000' -TimeoutSec 3 -UseBasicParsing | Out-Null; Write-Host '✓ Flask 後端運行正常' } catch { Write-Host '⚠ Flask 後端啟動中...' }"
powershell -command "try { Invoke-WebRequest -Uri 'http://localhost:3000' -TimeoutSec 3 -UseBasicParsing | Out-Null; Write-Host '✓ Nuxt3 前端運行正常' } catch { Write-Host '⚠ Nuxt3 前端啟動中...' }"

echo.
echo [3/3] 啟動 Electron 應用程式...
echo.

:: Start Electron app
npm start

echo.
echo ========================================
echo 應用程式已關閉
echo ========================================

:: Clean up background processes when Electron closes
echo 正在清理背景程序...
echo 停止 Flask 後端...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Flask Backend*" >nul 2>&1
echo 停止 Nuxt3 前端...
taskkill /f /im node.exe /fi "WINDOWTITLE eq Nuxt3 Frontend*" >nul 2>&1

echo 清理完成，按任意鍵退出...
pause >nul 