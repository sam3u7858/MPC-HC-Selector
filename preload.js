const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // App info
    getAppVersion: () => ipcRenderer.invoke('get-app-version'),

    // File operations
    showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
    showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
    writeFile: (filePath, data) => ipcRenderer.invoke('write-file', filePath, data),
    readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),

    // Menu events listeners
    onMenuAction: (callback) => {
        const menuEvents = [
            'menu-new-project',
            'menu-open-project', 
            'menu-save-project',
            'menu-export-clips',
            'menu-fetch-timestamp',
            'menu-add-clip',
            'menu-settings'
        ];

        menuEvents.forEach(event => {
            ipcRenderer.on(event, callback);
        });
    },

    // Remove menu event listeners
    removeMenuListeners: () => {
        const menuEvents = [
            'menu-new-project',
            'menu-open-project',
            'menu-save-project', 
            'menu-export-clips',
            'menu-fetch-timestamp',
            'menu-add-clip',
            'menu-settings'
        ];

        menuEvents.forEach(event => {
            ipcRenderer.removeAllListeners(event);
        });
        
        // Also remove global shortcut listeners
        ipcRenderer.removeAllListeners('global-shortcut');
    },

    // Global shortcut events listener
    onGlobalShortcut: (callback) => {
        console.log('*** PRELOAD: Setting up global shortcut listener');
        
        // Remove any existing listeners first
        ipcRenderer.removeAllListeners('global-shortcut');
        
        ipcRenderer.on('global-shortcut', (event, action) => {
            console.log('*** PRELOAD: Received global-shortcut event with action:', action);
            console.log('*** PRELOAD: Event details:', event);
            
            // Call the callback with the action
            try {
                callback(action);
            } catch (error) {
                console.error('*** PRELOAD: Error in callback:', error);
            }
        });
        
        console.log('*** PRELOAD: Global shortcut listener registered');
    },

    // System info
    platform: process.platform,
    
    // Environment
    isDev: process.env.NODE_ENV === 'development'
});

// Window controls API
contextBridge.exposeInMainWorld('windowAPI', {
    minimize: () => ipcRenderer.invoke('window-minimize'),
    maximize: () => ipcRenderer.invoke('window-maximize'), 
    close: () => ipcRenderer.invoke('window-close'),
    isMaximized: () => ipcRenderer.invoke('window-is-maximized')
});

// Flask API communication
contextBridge.exposeInMainWorld('flaskAPI', {
    // Base Flask server URL
    baseURL: 'http://localhost:5000',
    
    // Wrapper for fetch to Flask endpoints
    request: async (endpoint, options = {}) => {
        const url = `http://localhost:5000${endpoint}`;
        
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Flask API request failed:', error);
            throw error;
        }
    }
}); 