const { app, BrowserWindow, ipcMain, Menu, shell, dialog, globalShortcut } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Keep a global reference of the window object
let mainWindow;
let flaskProcess;

function createWindow() {
    // Create the browser window
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            enableRemoteModule: false,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, 'assets', 'icon.png'),
        titleBarStyle: 'default',
        show: false
    });

    // Set application menu
    createMenu();

    // Load the app
    const isDev = process.env.NODE_ENV === 'development';
    
    if (isDev) {
        // Development mode - load from localhost
        mainWindow.loadURL('http://localhost:3000');
        // Open DevTools in development
        mainWindow.webContents.openDevTools();
    } else {
        // Production mode - load from built files
        mainWindow.loadFile(path.join(__dirname, 'frontend', 'dist', 'index.html'));
    }

    // Show window when ready to prevent visual flash
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        
        // Focus on window
        if (isDev && process.platform === 'darwin') {
            mainWindow.focus();
        }
    });

    // Handle window closed
    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Handle external links
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });
}

function createMenu() {
    const template = [
        {
            label: '檔案',
            submenu: [
                {
                    label: '新增專案',
                    accelerator: 'CmdOrCtrl+N',
                    click: () => {
                        mainWindow.webContents.send('menu-new-project');
                    }
                },
                {
                    label: '開啟專案',
                    accelerator: 'CmdOrCtrl+O',
                    click: () => {
                        mainWindow.webContents.send('menu-open-project');
                    }
                },
                {
                    label: '儲存專案',
                    accelerator: 'CmdOrCtrl+S',
                    click: () => {
                        mainWindow.webContents.send('menu-save-project');
                    }
                },
                { type: 'separator' },
                {
                    label: '匯出片段',
                    accelerator: 'CmdOrCtrl+E',
                    click: () => {
                        mainWindow.webContents.send('menu-export-clips');
                    }
                },
                { type: 'separator' },
                {
                    label: process.platform === 'darwin' ? '結束 Clip Marker' : '結束',
                    accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
        },
        {
            label: '編輯',
            submenu: [
                {
                    label: '復原',
                    accelerator: 'CmdOrCtrl+Z',
                    role: 'undo'
                },
                {
                    label: '重做',
                    accelerator: 'Shift+CmdOrCtrl+Z',
                    role: 'redo'
                },
                { type: 'separator' },
                {
                    label: '剪下',
                    accelerator: 'CmdOrCtrl+X',
                    role: 'cut'
                },
                {
                    label: '複製',
                    accelerator: 'CmdOrCtrl+C',
                    role: 'copy'
                },
                {
                    label: '貼上',
                    accelerator: 'CmdOrCtrl+V',
                    role: 'paste'
                }
            ]
        },
        {
            label: '檢視',
            submenu: [
                {
                    label: '重新載入',
                    accelerator: 'CmdOrCtrl+R',
                    click: () => {
                        mainWindow.reload();
                    }
                },
                {
                    label: '強制重新載入',
                    accelerator: 'CmdOrCtrl+Shift+R',
                    click: () => {
                        mainWindow.webContents.reloadIgnoringCache();
                    }
                },
                {
                    label: '開發者工具',
                    accelerator: process.platform === 'darwin' ? 'Alt+Cmd+I' : 'Ctrl+Shift+I',
                    click: () => {
                        mainWindow.webContents.toggleDevTools();
                    }
                },
                { type: 'separator' },
                {
                    label: '實際大小',
                    accelerator: 'CmdOrCtrl+0',
                    role: 'resetzoom'
                },
                {
                    label: '放大',
                    accelerator: 'CmdOrCtrl+Plus',
                    role: 'zoomin'
                },
                {
                    label: '縮小',
                    accelerator: 'CmdOrCtrl+-',
                    role: 'zoomout'
                },
                { type: 'separator' },
                {
                    label: '全螢幕',
                    accelerator: process.platform === 'darwin' ? 'Ctrl+Cmd+F' : 'F11',
                    role: 'togglefullscreen'
                }
            ]
        },
        {
            label: '工具',
            submenu: [
                {
                    label: '從 MPC-HC 獲取時間',
                    accelerator: 'CmdOrCtrl+T',
                    click: () => {
                        mainWindow.webContents.send('menu-fetch-timestamp');
                    }
                },
                {
                    label: '新增片段',
                    accelerator: 'CmdOrCtrl+A',
                    click: () => {
                        mainWindow.webContents.send('menu-add-clip');
                    }
                },
                { type: 'separator' },
                {
                    label: '設定',
                    accelerator: 'CmdOrCtrl+,',
                    click: () => {
                        mainWindow.webContents.send('menu-settings');
                    }
                }
            ]
        },
        {
            label: '說明',
            submenu: [
                {
                    label: '關於 Clip Marker',
                    click: () => {
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: '關於 Clip Marker',
                            message: 'Clip Marker',
                            detail: '版本 1.0.0\n\n一個強大的影片片段標記工具，使用 Nuxt3 + Electron + Flask 架構開發。\n\n支援與 MPC-HC 整合，方便快速標記影片片段。',
                            buttons: ['確定']
                        });
                    }
                },
                {
                    label: '使用說明',
                    click: () => {
                        shell.openExternal('https://github.com/your-repo/clip-marker#readme');
                    }
                },
                { type: 'separator' },
                {
                    label: '回報問題',
                    click: () => {
                        shell.openExternal('https://github.com/your-repo/clip-marker/issues');
                    }
                }
            ]
        }
    ];

    // macOS specific menu adjustments
    if (process.platform === 'darwin') {
        template.unshift({
            label: app.getName(),
            submenu: [
                {
                    label: '關於 ' + app.getName(),
                    role: 'about'
                },
                { type: 'separator' },
                {
                    label: '服務',
                    role: 'services',
                    submenu: []
                },
                { type: 'separator' },
                {
                    label: '隱藏 ' + app.getName(),
                    accelerator: 'Command+H',
                    role: 'hide'
                },
                {
                    label: '隱藏其他',
                    accelerator: 'Command+Shift+H',
                    role: 'hideothers'
                },
                {
                    label: '顯示全部',
                    role: 'unhide'
                },
                { type: 'separator' },
                {
                    label: '結束',
                    accelerator: 'Command+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
        });
    }

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

function startFlaskServer() {
    const isDev = process.env.NODE_ENV === 'development';
    const pythonPath = isDev ? 'python' : path.join(process.resourcesPath, 'backend', 'python');
    const flaskApp = isDev ? 
        path.join(__dirname, 'backend', 'app.py') : 
        path.join(process.resourcesPath, 'backend', 'app.py');

    console.log('Starting Flask server...');
    flaskProcess = spawn(pythonPath, [flaskApp], {
        stdio: ['pipe', 'pipe', 'pipe']
    });

    flaskProcess.stdout.on('data', (data) => {
        console.log(`Flask stdout: ${data}`);
    });

    flaskProcess.stderr.on('data', (data) => {
        console.error(`Flask stderr: ${data}`);
    });

    flaskProcess.on('close', (code) => {
        console.log(`Flask process exited with code ${code}`);
    });
}

function stopFlaskServer() {
    if (flaskProcess) {
        flaskProcess.kill();
        flaskProcess = null;
    }
}

function registerGlobalShortcuts() {
    console.log('Starting global shortcuts registration...');
    
    // Register global shortcuts for MPC-HC integration
    const shortcuts = [
        {
            key: 'Ctrl+Shift+S',
            action: 'get-start-time',
            description: '獲取開始時間'
        },
        {
            key: 'Ctrl+Shift+D', 
            action: 'get-end-time',
            description: '獲取結束時間'
        },
        {
            key: 'Ctrl+Shift+N',
            action: 'name-clip',
            description: '輸入名稱並新增片段'
        },
        {
            key: 'Ctrl+Shift+B',
            action: 'quick-add-clip',
            description: '快速新增片段（自動命名）'
        },
        {
            key: 'Ctrl+Shift+E',
            action: 'export-clips',
            description: '匯出片段'
        }
    ];

    let registeredCount = 0;
    shortcuts.forEach(shortcut => {
        try {
            console.log(`Attempting to register: ${shortcut.key}`);
            
            const ret = globalShortcut.register(shortcut.key, () => {
                console.log(`*** GLOBAL SHORTCUT TRIGGERED: ${shortcut.key} - ${shortcut.description} ***`);
                
                // Optionally focus the window only for add-clip (Ctrl+Shift+N)
                if (mainWindow && !mainWindow.isDestroyed()) {
                    if (shortcut.action === 'name-clip') {
                        console.log('Bringing window to front for name-clip');
                        if (mainWindow.isMinimized()) {
                            mainWindow.restore();
                        }
                        mainWindow.show();
                        mainWindow.focus();
                    }

                    // Send the action to the renderer process regardless of focus state
                    mainWindow.webContents.send('global-shortcut', shortcut.action);
                    console.log(`Sent "global-shortcut" event with action: ${shortcut.action}`);
                } else {
                    console.log('Main window not available');
                }
            });

            if (!ret) {
                console.error(`❌ Failed to register global shortcut: ${shortcut.key}`);
            } else {
                console.log(`✅ Successfully registered: ${shortcut.key} - ${shortcut.description}`);
                registeredCount++;
            }
        } catch (error) {
            console.error(`❌ Error registering global shortcut ${shortcut.key}:`, error);
        }
    });
    
    console.log(`Global shortcuts registration complete: ${registeredCount}/${shortcuts.length} shortcuts registered`);
    
    // Test if any shortcuts are currently registered
    console.log('Currently registered shortcuts:', globalShortcut.isRegistered('Ctrl+Alt+S') ? 'Ctrl+Alt+S registered' : 'Ctrl+Alt+S not registered');
}

function unregisterGlobalShortcuts() {
    // Unregister all global shortcuts
    globalShortcut.unregisterAll();
    console.log('All global shortcuts unregistered');
}

// IPC handlers
ipcMain.handle('get-app-version', () => {
    return app.getVersion();
});

ipcMain.handle('show-save-dialog', async (event, options) => {
    const result = await dialog.showSaveDialog(mainWindow, options);
    return result;
});

ipcMain.handle('show-open-dialog', async (event, options) => {
    const result = await dialog.openDialog(mainWindow, options);
    return result;
});

ipcMain.handle('write-file', async (event, filePath, data) => {
    try {
        fs.writeFileSync(filePath, data, 'utf8');
        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('read-file', async (event, filePath) => {
    try {
        const data = fs.readFileSync(filePath, 'utf8');
        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

// App event handlers
app.whenReady().then(() => {
    createWindow();
    startFlaskServer();
    registerGlobalShortcuts();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        unregisterGlobalShortcuts();
        stopFlaskServer();
        app.quit();
    }
});

app.on('before-quit', () => {
    unregisterGlobalShortcuts();
    stopFlaskServer();
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
    contents.on('new-window', (event, navigationUrl) => {
        event.preventDefault();
        shell.openExternal(navigationUrl);
    });
}); 