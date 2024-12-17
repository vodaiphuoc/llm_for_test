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
        status_panel += `<ul class="list-group" id="task-1"><strong>${task_params[index]['name']}</strong></ul>`;
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
