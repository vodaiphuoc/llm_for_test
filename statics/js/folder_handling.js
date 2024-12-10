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
        .then(folderTree => post_processing(folderTree))
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
}

function py_file_trigger (file_name) {
    console.log('run index in apis.js function: ', file_name);
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
                $(".test_index_api").html(`<div>${data['html_content']}</div>`);
            });
        }
        
    });
}

function add_actions_on_file_py () {
    var py_files = document.getElementsByClassName("py_file");
    var i;
    console.log('py file ready', py_files.length);
    for (i = 0; i < py_files.length; i++) {
        py_files[i].addEventListener("click", function(e) {
            e.preventDefault();
            py_file_trigger(this.id);
        });
    }
}

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