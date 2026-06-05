const { app, BrowserWindow } = require('electron')
const path = require('node:path')
const fs = require('node:fs')

function createWindow() {
  const win = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1180,
    minHeight: 760,
    backgroundColor: '#0a0a0c',
    title: 'ACV Gesture Control',
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  const buildIndex = path.join(__dirname, '..', 'dist', 'index.html')
  if (fs.existsSync(buildIndex) && !process.env.ELECTRON_START_URL) {
    win.loadFile(buildIndex)
    return
  }

  win.loadURL(process.env.ELECTRON_START_URL || 'http://127.0.0.1:5173')
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
