/**
 * Script use by Front End
 */
$('body').ready(function () {
    $(document).on('click', '#open-folder-button', function(event){
        /**
         * Clear text in `#folder-tree` and `.show_py_content` first
         */
        let folder_tree = $('#folder-tree');
        folder_tree.html("<div></div>");

        let current_open_py = $('.show_py_content');
        current_open_py.html("<div></div>");

        /**
         * Get data data from express js server
         */
        let myHeaders = new Headers({
            "Content-Type": "application/json",
            "referrer": "http://127.0.0.1:5000",
        });
        fetch('http://127.0.0.1:5000/open',{
            method: 'GET',
            headers: myHeaders,
        })
        .then(respone=> respone.json())
        .then(respone_dict => post_processing(respone_dict))
        .catch((error)=>{
            console.log(error);
        });

    });
});

function post_processing(respone_dict) {
    // step 1
    let tree_wrapper = 
        `<ul id="root-tree">
            REPLACE
        </ul>
        `;
    
    const path2currentDir = respone_dict['path2currentDir'];
    const currentFolder = respone_dict['currentFolder'];
    set_current_directory(path2currentDir, currentFolder);

    const folderTree = respone_dict['folder_tree'];
    let tree_string = ``;
    for (var key in folderTree){
        // concat to initial string
        tree_string += make_tree_content(key, folderTree[key], key);
    }
    // Place new built string to wrapper ul tag
    tree_wrapper = tree_wrapper.replace('REPLACE',tree_string);
    tree_wrapper = $(tree_wrapper);
    
    // update content
    let folder_tree = $('#folder-tree');
    folder_tree.html(tree_wrapper);

    // Step 2
    add_actions_on_tree_element();

    add_actions_on_file_py();

    // Check open folder status: indent in files and .txt file
    uploadFile_reponse = respone_dict['reponse_uploadFiles'];
    console.log('reponse_uploadFiles',uploadFile_reponse);
    UploadFilesStatus(uploadFile_reponse, "show_test_cases",".");

}

function py_file_trigger (file_name) {
    
    let myHeaders = new Headers({
        "Content-Type": "application/json",
    });

    url_query = encodeURI(`http://127.0.0.1:8000/load_py/?file_name=${file_name}`);
    fetch(url_query, {
        method: 'GET',
        headers: myHeaders
    })
    .then((response)=> {
        if (response.ok) {
            response.json()
            .then((data)=>{
                $(".show_py_content").html(`${data['html_content']}`);
            });
        } else {
            response.json()
            .then((data)=>{
                $(".show_py_content").html(`${data['html_content']}`);
            });
        }
        
    });
}

function add_actions_on_file_py () {
    var py_files = document.getElementsByClassName("py_file");
    var i;
    for (i = 0; i < py_files.length; i++) {
        py_files[i].addEventListener("click", function(e) {
            e.preventDefault();
            py_file_trigger(this.id);
        });
    }
}
