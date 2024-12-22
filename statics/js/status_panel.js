/**
 * Create status panel
 * @param {str} parent_selector_name class or id of parent element which contains this status panel
 * @param {str} selector_type determine the selector is calss or id
 * @param {dictionary} task_params taks configuration
 * @example
 * 1) parent tag <div class="show_test_cases">
 * parent_selector_name = show_test_cases
 * selector_type = .
 * 2) parent tag <div id=".show_test_cases">
 * parent_selector_name = show_test_cases
 * selector_type = #
 * @returns {null} this function not return any thing
 */
function init_status_panel (parent_selector_name, selector_type, task_params) {
    let status_panel = '<div class="status"><div style="text-align:center"><strong>Status</strong></div>';

    task_params.forEach((task_param, index)=>{
        status_panel += `<ul class="list-group" id=${task_params[index]['selector']}><strong>${task_params[index]['name']}</strong></ul>`;
    });

    status_panel += '</div>';

    $(`${selector_type}${parent_selector_name}`).html(status_panel);
}

/**
 * Clear the status pannel
 * @param {str} parent_selector_name
 * @param {str} selector_type
 * see {@link init_status_panel} for descriptions of parameter inputs
 */
function clear_status_panel (parent_selector_name, selector_type) {
    $(`${selector_type}${parent_selector_name} .status`).remove();
}


/**
 * Return HTMLElement for showing done icon
 * @returns {str} string represent done icon in svg tag
 */
function get_done_icon () {
    return `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="green" class="bi bi-check2-circle" viewBox="0 0 16 16">
    <path d="M2.5 8a5.5 5.5 0 0 1 8.25-4.764.5.5 0 0 0 .5-.866A6.5 6.5 0 1 0 14.5 8a.5.5 0 0 0-1 0 5.5 5.5 0 1 1-11 0"/>
    <path d="M15.354 3.354a.5.5 0 0 0-.708-.708L8 9.293 5.354 6.646a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0z"/>
    </svg>`
}

function get_ok_icon (size = 14) {
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" fill="green" class="bi bi-emoji-smile" viewBox="0 0 16 16">
    <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>
    <path d="M4.285 9.567a.5.5 0 0 1 .683.183A3.5 3.5 0 0 0 8 11.5a3.5 3.5 0 0 0 3.032-1.75.5.5 0 1 1 .866.5A4.5 4.5 0 0 1 8 12.5a4.5 4.5 0 0 1-3.898-2.25.5.5 0 0 1 .183-.683M7 6.5C7 7.328 6.552 8 6 8s-1-.672-1-1.5S5.448 5 6 5s1 .672 1 1.5m4 0c0 .828-.448 1.5-1 1.5s-1-.672-1-1.5S9.448 5 10 5s1 .672 1 1.5"/>
    </svg>`
}

function get_ng_icon (size = 14) {
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" fill="red" class="bi bi-emoji-frown" viewBox="0 0 16 16">
    <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>
    <path d="M4.285 12.433a.5.5 0 0 0 .683-.183A3.5 3.5 0 0 1 8 10.5c1.295 0 2.426.703 3.032 1.75a.5.5 0 0 0 .866-.5A4.5 4.5 0 0 0 8 9.5a4.5 4.5 0 0 0-3.898 2.25.5.5 0 0 0 .183.683M7 6.5C7 7.328 6.552 8 6 8s-1-.672-1-1.5S5.448 5 6 5s1 .672 1 1.5m4 0c0 .828-.448 1.5-1 1.5s-1-.672-1-1.5S9.448 5 10 5s1 .672 1 1.5"/>
    </svg>`
}

function get_exclamation (size = 12) {
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" fill="currentColor" class="bi bi-exclamation-circle" viewBox="0 0 16 16">
    <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>
    <path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0M7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0z"/>
    </svg>`
}


/**
 * Update process in status panel
 * @param {Generate} task_object- instance of Generate
 */
function status_update_panel (task_object) {
    let current_value = $(`.status ul#${task_object.id_selector}`);
    
    if (task_object.is_created && $(`.status ul li#${task_object.id_selector}-created`).length === 0) {
        current_value.append(`<li class="list-group-item list-group-item-secondary" id="${task_object.id_selector}-created">
                                <span class="sr-only">${task_object.task_name} is created</span>
                                ${get_done_icon()}
                            </li>`);

    } else if (task_object.is_execute && $(`.status li#${task_object.id_selector}-execute`).length === 0) {
        current_value.append(`<li class="list-group-item list-group-item-secondary" id="${task_object.id_selector}-execute">
                                <span class="sr-only">${task_object.task_name} processing ...</span>
                                <div class="spinner-border text-primary spinner-border-sm" role="status"></div>
                            </li>`);

    } else if (task_object.is_done && $(`.status li#${task_object.id_selector}-done`).length === 0) {
        $(`.status li#${task_object.id_selector}-execute`).html(`<span class="sr-only">${task_object.task_name} processing </span>
                                                                ${get_done_icon()}`);

        current_value.append(`<li class="list-group-item list-group-item-secondary" id="${task_object.id_selector}-done"
            ><span class="sr-only">${task_object.task_name} is Done</span>
            ${get_done_icon()}
            </li>`);
    }
}


/** 
 * @param {dictionary} uploadFile_reponse :
 * 1) `Array[Array[str,dictionary]]` indent_check - 
 * 2) `Array[str]` require_txt_check - 
 */
function UploadFilesStatus (uploadFile_reponse, parent_selector_name, selector_type) {
    const indent_checklist = uploadFile_reponse['indent_check'];
    const require_txt_check = uploadFile_reponse['require_txt_check'];

    // initialize element first
    let status_panel = `<div class="status">
                            <div style="text-align:center"><strong>Scan Your Repo</strong></div>
                            <ul class="list-group" id="indent_check" 
                                data-toggle="tooltip" title="No indentation error helps run Pytest better!">
                                <strong>Indent Errors ${get_exclamation()}</strong>
                            </ul>
                            <ul class="list-group" id="require_txt_check"
                                data-toggle="tooltip" title="Provide PyPi helps install correct packages!">
                                <strong>Requirement file ${get_exclamation()}</strong>
                            </ul>
                        </div>`;
    $(`${selector_type}${parent_selector_name}`).html(status_panel);

    // append on condition
    if (indent_checklist.length > 0) {
        $(`ul#indent_check`).append(`<span class="sr-only">
            Found ${indent_checklist.length} indent error${(indent_checklist.length === 1) ? "" : "s"} ${get_ng_icon()}
            </span>`);
        // append for each file
        indent_checklist.forEach((each_error, index)=>{
            $(`ul#indent_check`).append(`<li class="list-group-item list-group-item-secondary" 
                                        id="indent-${index}">
                                        <ul>
                                            <li><span class="sr-only">File: ${indent_checklist[index][0]}</span></li>
                                            <li><span class="sr-only">Line number: ${indent_checklist[index][1]['line_number']}</span></li>
                                        </ul>
                                        </li>`);
        });
    
    } else {
        $(`ul#indent_check`).append(`<li class="list-group-item list-group-item-secondary">
                                    <span class="sr-only">No indent error found</span>${get_ok_icon()}
                                    </li>`);
    }

    // append on condition
    if (require_txt_check.length > 0) {
        $(`ul#require_txt_check`).append(`<span class="sr-only">
                                        Found ${require_txt_check.length} requirement file${(require_txt_check.length===1) ? "" : "s"}
                                        ${get_ok_icon()}</span>`);
        require_txt_check.forEach((each_error, index)=>{
            $(`ul#require_txt_check`).append(`<li class="list-group-item list-group-item-secondary" 
                                        id="requirement-${index}">
                                        <ul>
                                            <li><span class="sr-only">File: ${require_txt_check[index]}</span></li>
                                        </ul>
                                        </li>`);
        });

    } else {
        status_panel += `<li class="list-group-item list-group-item-secondary">
                        <span class="sr-only">No indent error found</span>${get_ng_icon()}
                        </li>`;
    }
    



}

