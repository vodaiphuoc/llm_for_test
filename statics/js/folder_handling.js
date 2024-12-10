/*
This module contains functions for processing files when user browsers their folders
Steps:
    1) get all file directories from input tag HTML
    2) send directories to back-end with api
    3) update `#folder-tree` div content
    4) add eventlistener to each folder on `#folder-tree`
*/

/**
 * Send to nodejs server port 50000
 */
$('body').ready(function () {
    $(document).on('click', '#open-folder-button', function(event){
        console.log('run............');
        let myHeaders = new Headers({
            "Content-Type": "application/json",
            "referrer": "http://127.0.0.1:8000",
            
        });
        fetch('http://127.0.0.1:5000/open',{
            method: 'GET',
            headers: myHeaders,
            mode: 'cors'
        })
        .then((respone)=>{
            console.log(respone);
            const file_list = respone.body;
            console.log(file_list);

            send_directories(file_list);
            // post_processing(file_list);
        })
        .catch((error)=>{
            console.log(error);
        });

    });
});


function post_processing(file_list) {
    const folderTree = get_folder_tree(file_list);

    // Step 3
    send_directories(folderTree);

    let tree_wrapper = 
        `<ul id="root-tree">
            REPLACE
        </ul>
        `;
    let tree_string = ``;
    for (var key in folderTree){
        // concat to initial string
        tree_string += make_tree_content(key, folderTree[key]);
    }
    // Place new built string to wrapper ul tag
    tree_wrapper = tree_wrapper.replace('REPLACE',tree_string);
    tree_wrapper = $(tree_wrapper);
    
    // update content
    let folder_tree = $('#folder-tree');
    folder_tree.replaceWith(tree_wrapper);

    // Step 4
    add_actions_on_tree_element();

}

function get_folder_tree (file_list) {
    /** 
     * Create folder tree structure in form of dictionary
     */
    const folderTree = {};
    for (const file of file_list) {
        let dir = file.webkitRelativePath;

        if ((dir.search('/__pycache__/') === -1) && (dir.search('__init__') === -1)) {
            const parts = dir.split('/');
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


function send_directories (folders_as_tree) {
    console.log('send api');
    let myHeaders = new Headers({
        "Content-Type": "application/json",
    });

    fetch('http://localhost:8000/upload_files', {
        method: 'POST',
        body: JSON.stringify({
            'dir': folders_as_tree,
        }),
        mode: 'cors',
        headers: myHeaders
    })
    .catch((error)=>{
        console.log(error);
    });
}


function make_tree_content(key, value) {
    /**
     * Recursive function creates only string for folder case or file .py case
     * Args:
     * - key: int, key of dictionary
     * - value: Union[str, dict]
    Return:
        - str
     */

    let content_element = '';
    if ( typeof value !== "string") {
        // folder case
        content_element = 
            `<li><span class="folder-in-tree">FOLDER_NAME</span>
                <ul class="nested">
                    REPLACE
                </ul>
            </li>
            `;
        content_element = content_element.replace('FOLDER_NAME', key);
        
        let tree_string = ``;
        for (var k in value){
            tree_string += make_tree_content(k, value[k]);
        }
        content_element = content_element.replace('REPLACE', tree_string);

    } else {
        // file .py case
        content_element = `<li class= "py_file">FILE_NAME</li>`;
        content_element = content_element.replace('FILE_NAME', key);   
    }
    
    return content_element;
}


function add_actions_on_tree_element () {
    /**
     * Add eventlistener to each folder
     */
    var toggler = document.getElementsByClassName("folder-in-tree");
    var i;
    console.log(toggler);
    for (i = 0; i < toggler.length; i++) {
        toggler[i].addEventListener("click", function() {
            this.parentElement.querySelector(".nested").classList.toggle("active");
            this.classList.toggle("folder-in-tree-down");
        });
    }
};


function close_folder_tree () {
    /**
     * Clear text in `#folder-tree`
     */
    $('#folder-tree').val("jfialjvlmvkla");
}

// when user click file to read
$('#folder-tree').ready(()=>{
    $(document).on('click', '.py_file',()=>{
        console.log($('.py_file').text);
    });
});