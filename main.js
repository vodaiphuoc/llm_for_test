const { app, BrowserWindow } = require('electron/main');
const path = require('node:path');
let {PythonShell} = require('python-shell');

const createWindow = () => {
    const win = new BrowserWindow({
    // width: 800,
    // height: 600,
	movable: false,
    resizable: false,
    maximizable: false,
    minimizable: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
    });
    win.loadFile('./templates/index.html');
    win.maximize();
}


app.whenReady().then(() => {
    // start python fastapi server
    let options = {
        mode: 'text',
        pythonPath: 'myenv/Scripts/python.exe',
        pythonOptions: ['-u'], // get print results in real-time
        scriptPath: 'back_end'
      };
    PythonShell.run('main.py', options);
    
    // create main window of app
    createWindow();

});

// close app
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
        process.kill(process.pid, 'SIGINT');
        
    }
});