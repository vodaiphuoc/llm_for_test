/**
 * Script use by Front End
 */
$('body').ready(function () {
    $(document).on('click', '#open-folder-button', function(event){
        console.log('run............');
        let myHeaders = new Headers({
            "Content-Type": "application/json",
            "referrer": "http://127.0.0.1:5000",
        });
        fetch('http://127.0.0.1:5000/open',{
            method: 'GET',
            headers: myHeaders,
        })
        .then(respone=> respone.json())
        .then(file_list => post_processing(file_list))
        .catch((error)=>{
            console.log(error);
        });

    });
});

function post_processing(folderTree) {
    // step 1
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
    folder_tree.html(tree_wrapper);

    // Step 2
    add_actions_on_tree_element();
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
    for (i = 0; i < toggler.length; i++) {
        toggler[i].addEventListener("click", function() {
            this.parentElement.querySelector(".nested").classList.toggle("active");
            this.classList.toggle("folder-in-tree-down");
        });
    }
};

$('body').ready(function () {
    /**
     * Clear text in `#folder-tree`
     */
    $(document).on('click', '#close-folder-button', function(event){
        let folder_tree = $('#folder-tree');
        console.log(folder_tree);
        folder_tree.html("<div></div>");
    });
    
});