function set_current_directory (path2currentDir,currentFolder) {
    const update_dir = `${path2currentDir}${currentFolder}`;
    $('#currentDir').text(update_dir);
}

function make_tree_content(key, value, parent_key) {
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
            tree_string += make_tree_content(k, value[k], `${parent_key}PATHSPLIT${k}`);
        }
        content_element = content_element.replace('REPLACE', tree_string);

    } else {
        // file .py case
        content_element =  `<div>
                                <div style="display:inline-grid;">
                                    <li class= "py_file" id=${parent_key} style="display: inline-flex;">
                                    FILE_NAME
                                    </li>
                                </div>
                                <div style="display:inline-grid;float: right;">
                                    <input class="form-check-input" type="checkbox" value="" id=${parent_key}>
                                </div>
                            </div>`;
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
    for (i = 0; i < toggler.length; i++) {
        toggler[i].addEventListener("click", function() {
            this.parentElement.querySelector(".nested").classList.toggle("active");
            this.classList.toggle("folder-in-tree-down");
        });
    }
};
