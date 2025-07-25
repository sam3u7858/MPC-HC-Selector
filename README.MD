
# Clip Marker - Electron 版本

一個強大的影片片段標記工具，使用 **Nuxt3 + Electron + Flask** 架構開發，支援與 MPC-HC 整合。

## 🚀 特色功能

- **現代化介面**: 使用 Nuxt3 和 Tailwind CSS 打造的美觀介面
- **深色模式**: 支援淺色/深色主題切換
- **MPC-HC 整合**: 即時獲取播放器時間戳記
- **桌面應用**: Electron 打包的原生桌面應用程式
- **API 後端**: Flask 提供強大的後端 API 支援
- **自動儲存**: 自動儲存工作進度，防止資料遺失
- **快捷鍵支援**: 豐富的鍵盤快捷鍵
- **多語言**: 支援繁體中文界面

## 🛠️ 技術架構

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│                 │    │                  │    │                 │
│   Nuxt3 前端    │◄──►│  Electron 主程序  │◄──►│  Flask 後端      │
│   (Vue 3)       │    │   (Node.js)      │    │   (Python)      │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                        │                        │
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  TailwindCSS    │    │   IPC 通訊        │    │   MPC-HC API    │
│  Pinia Store    │    │   檔案系統操作     │    │   影片剪輯 API   │
│  響應式設計      │    │   選單控制        │    │   自動儲存      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 系統需求

### 必要軟體

- **Node.js** 18.0 或更高版本 ([下載](https://nodejs.org/))
- **Python** 3.8 或更高版本 ([下載](https://www.python.org/downloads/))
- **MPC-HC** 影片播放器 ([下載](https://mpc-hc.org/))

### 開發依賴

- npm 或 yarn
- Git

## 🔧 安裝與設定

### 1. 快速開始

1. **下載專案**

   ```bash
   git clone <repository-url>
   cd electron_test
   ```

2. **設定 Flask 後端**

   ```bash
   # 執行 Flask 設定腳本（會自動建立虛擬環境）
   setup-flask.bat
   ```

3. **啟動應用程式**

   **方式一：生產模式啟動（推薦）**

   ```bash
   # 使用靜態檔案，只啟動 Flask 後端 + Electron
   run-simple.bat
   ```

   **方式二：開發模式啟動**

   ```bash
   # 啟動 Flask + Nuxt3 開發伺服器 + Electron
   run.bat
   ```

   **方式三：完整開發模式**

   ```bash
   # 完整開發環境（包含所有伺服）
   startup-web-version.bat
   ```

### 2. 手動安裝

如果自動腳本無法執行，可以手動進行安裝：

#### 安裝 Electron 依賴

```bash
npm install
```

#### 安裝前端依賴

```bash
cd frontend
npm install
cd ..
```

#### 設定 Flask 後端

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

#### 啟動開發伺服器

```bash
# 終端 1: 啟動 Flask 後端
cd backend
venv\Scripts\activate
python app.py

# 終端 2: 啟動 Nuxt3 前端
cd frontend
npm run dev

# 終端 3: 啟動 Electron
npm run dev:electron
```

## 🎮 使用方法

### 基本操作

