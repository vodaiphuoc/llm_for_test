/**
 * This module defines express js apis and 
 * support functions on nodejs server-side
 */

function walk(path2currentDir,currentDirPath, callback) {
    var fs = require('fs'),
    path = require('path');

    const file_list = [];
    
    const files = fs.readdirSync(currentDirPath);
    files.forEach(function (name) {
        var filePath = path.join(currentDirPath, name);
        var stat = fs.statSync(filePath);
        if (stat.isFile()) {
            let sub_file = callback(filePath, stat);
            sub_file = sub_file.replace(path2currentDir,'');
            file_list.push(sub_file);
        } else if (stat.isDirectory()) {
            const sub_files = walk(path2currentDir,filePath, callback);
            file_list.push(...sub_files);
        }
    });
    return file_list
}

function get_folder_tree (file_list) {
    /** 
     * Create folder tree structure in form of dictionary
     */
    const folderTree = {};
    for (const dir of file_list) {
        if ((dir.search('__pycache__') === -1) && (dir.search('__init__') === -1)) {
            const parts = dir.split('\\');
            let currentLevel = folderTree;

            parts.forEach((part, index) => {
                if (!currentLevel[part]) {
                    currentLevel[part] = {};
                }
                
                if (index === parts.length - 1) {
                    currentLevel[part] = part;
                } else {
                    currentLevel = currentLevel[part];
                }
            });

        } else {
            continue;
        }
        
    };
    return folderTree;
}

function send_directories (folders_as_tree, path2currentDir) {
    /**
     * Nodejs send data to fastapi server
     * send data:
     *  - dict_tree: dict
     *  - path2currDir: path to current selected folder by user
     * Example:
     *  - dict_tree: {'A': {'B': {...}, 'C': {...}, '**.py':'**.py'}}
     *  - path2currDir: 'C:\...\...\'-> 'A'
     */
    let myHeaders = new Headers({
        "Content-Type": "application/json",
    });

    fetch('http://127.0.0.1:8000/upload_files', {
        method: 'POST',
        body: JSON.stringify({
            'dict_tree': folders_as_tree,
            'path2currDir': path2currentDir
        }),
        mode: 'cors',
        headers: myHeaders
    })
    .catch((error)=>{
        console.log(error);
    });
}


function start_express () {
    /**
     * Define express server on port 5000
     */
    const { dialog } = require('electron');
    var express = require('express');
    var exp_app = express();
    // var cors = require('cors');
    // exp_app.use('/statics',express.static('statics'));
    // exp_app.use('/templates',express.static('templates'));

    // let corsOptions = {
    //     origin : ['http://localhost:5000'],
    // };

    // exp_app.use(cors(corsOptions));

    // only user this route for testing on Chrome
    // exp_app.get('/', function (req, res) {
    //     res.sendFile(path.join(__dirname, '/templates/index.html'));
    // });

    exp_app.get('/open', function (req, res) {
        /**
         * This route is sent from /statics/js/folder_handling.js/line 4
         */
        dialog.showOpenDialog({ properties: ['openDirectory']})
        .then((result)=>{
            const file_list = [];
            let currentFolder = null;
            let path2currentDir = null;
            if (result['canceled'] === false) {
                const currentDir = result['filePaths'][0];
                
                const splited_str = currentDir.split('\\');
                currentFolder= splited_str[splited_str.length-1];
                
                path2currentDir = result['filePaths'][0].replace(currentFolder,'');

                const result_file_list = walk(path2currentDir, currentDir, function(filePath, stat) {
                    return filePath
                });
                file_list.push(...result_file_list);

                return [file_list, path2currentDir, currentFolder]
            } else {
                return [file_list, "", ""]
            }
            
        })
        .then(([send_file_list, path2currentDir, currentFolder])=>{

            // convert list dir of files to dictionary
            const folder_tree = get_folder_tree(send_file_list);

            // send dict tree + path to current 
            // selected folder to python server
            send_directories(folder_tree, path2currentDir);

            // send dict tree back to front-end
            res.json({
                'folder_tree':folder_tree,
                'path2currentDir':path2currentDir,
                'currentFolder': currentFolder
            });
        });
    });

    var server = exp_app.listen(5000, function () {
        console.log("Express App running at http://127.0.0.1:5000/");
    });
}

module.exports = { start_express }