@echo off
echo ========================================
echo Clip Marker Flask Backend Setup
echo ========================================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤：未找到 Python，請先安裝 Python 3.8 或更高版本
    echo 下載地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python 已安裝，版本資訊：
python --version

:: Create virtual environment
echo.
echo 正在創建虛擬環境...
cd backend
if exist venv (
    echo 虛擬環境已存在，正在移除舊環境...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo 錯誤：無法創建虛擬環境
    pause
    exit /b 1
)

:: Activate virtual environment
echo 正在啟動虛擬環境...
call venv\Scripts\activate.bat

:: Upgrade pip
echo 正在升級 pip...
python -m pip install --upgrade pip

:: Install requirements
echo 正在安裝 Python 依賴套件...
pip install -r requirements.txt
if errorlevel 1 (
    echo 錯誤：無法安裝依賴套件
    pause
    exit /b 1
)

echo.
echo ========================================
echo Flask 後端設定完成！
echo ========================================
echo.
echo 虛擬環境位置：backend\venv
echo 啟動指令：cd backend && venv\Scripts\activate && python app.py
echo 或直接執行：startup-web-version.bat
echo.
pause 