const { app, BrowserWindow } = require('electron/main');
const path = require('node:path');
let {PythonShell} = require('python-shell');
const { dialog } = require('electron')


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
}


function walk(currentDirPath, callback) {
    var fs = require('fs'),
    path = require('path');

    const file_list = [];
    
    const files = fs.readdirSync(currentDirPath);
    files.forEach(function (name) {
        var filePath = path.join(currentDirPath, name);
        var stat = fs.statSync(filePath);
        if (stat.isFile()) {
            const sub_file = callback(filePath, stat);
            file_list.push(sub_file);
        } else if (stat.isDirectory()) {
            const sub_files = walk(filePath, callback);
            file_list.push(...sub_files);
        }
    });
    return file_list
}

const start_express = () => {
    var express = require('express');
    var exp_app = express();
    var cors = require('cors');

    let corsOptions = {
        origin : ['http://localhost:5000','http://127.0.0.1:8000/'],
    };

    exp_app.use(cors(corsOptions));

    exp_app.get('/open', function (req, res) {
        // res.send('Hello World');
        console.log("Express index route");

        res.json({'list':[1,2,3,4,6]});

        // dialog.showOpenDialog({ properties: ['openDirectory']})
        // .then((result)=>{
        //     const file_list = [];
        //     if (result['canceled'] === false) {
        //         const result_file_list = walk(result['filePaths'][0], function(filePath, stat) {
        //             return filePath
        //         });
        //         file_list.push(...result_file_list);
        //     }
        //     return file_list
        // })
        // .then((send_file_list)=>{
        //     res.json({'list':[1,2,3,4,6]});
        // });
    });

    var server = exp_app.listen(5000, function () {
        console.log("Express App running at http://127.0.0.1:5000/");
    })
}

app.whenReady().then(() => {
    // start python fastapi server
    // let options = {
    //     mode: 'text',
    //     pythonPath: 'myenv/Scripts/python.exe',
    //     pythonOptions: ['-u'], // get print results in real-time
    //     scriptPath: 'back_end'
    //   };
    // PythonShell.run('main.py', options);
    
    // create main window of app
    createWindow();
    
    // start nodejs server
    start_express();
});

// close app
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
        process.kill(process.pid, 'SIGINT');
        
    }
});