const { app, BrowserWindow } = require('electron/main');
const path = require('node:path');
let {PythonShell} = require('python-shell');
const { start_express } = require('./back_end/express_apis.js');

const createWindow = () => {
    const win = new BrowserWindow({
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
    win.webContents.openDevTools();
}

function start_py_server () {
    // start python fastapi server
    let options = {
        mode: 'text',
        pythonPath: 'myenv/Scripts/python.exe',
        pythonOptions: ['-u'], // get print results in real-time
        scriptPath: 'back_end'
      };
    PythonShell.run('main.py', options);
}


app.whenReady().then(() => {
    createWindow();
    start_express();
    start_py_server();
});

// close app
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
        process.kill(process.pid, 'SIGINT');
        
    }
});