/* Define status of generate button and call api to LLM */ 
$('body').ready(()=>{
    $(document).on('click', '#generate-button', function(event){
        
        
        // check all checkbox
        selected_py_files = [];
        $("input[id$='.py']").each((index, input_ele)=>{
            if (input_ele.checked === true) {
                selected_py_files.push(input_ele.id);
            }
        });
        if (selected_py_files.length === 0) {
            const get_ele = $('#empty-file-list-model');
            console.log(get_ele);

            const myModal = bootstrap.Modal.getOrCreateInstance('#empty-file-list-model');
            myModal.show();

        } else {
            setButtonLoadingState();
        
            const task_params = [
                {
                    'name':'Task 1',
                    'method': 'POST',
                    'request_data': {'file_list': selected_py_files},
                    'selector': 'task-1'
                },
                {
                    'name':'Task 2',
                    'method': 'GET',
                    'request_data': null,
                    'selector': 'task-2'
                },
                {
                    'name':'Task 3',
                    'method': 'GET',
                    'request_data': null,
                    'selector': 'task-3'
                },
                {
                    'name':'Task 4',
                    'method': 'GET',
                    'request_data': null,
                    'selector': 'task-4'
                },

            ];
            init_status_panel("show_test_cases",".",task_params);

            run_tasks(task_params)
            .then((value)=>{
                clear_status_panel("show_test_cases",".");
                setButtonNormalState();
                update_result(value);
            })
            .catch((error)=>{
                console.log(error);
            });
        }
       
    });
});


function update_result (data) {
    $('body').ready(()=>{
        console.log(data);
        if ($('.show_test_cases .status').length === 0) {
            $('.show_test_cases').append(`<div>My new data: ${data}</div>`);
        }
    })    
    
}


/**
 * Set status of button is loading
 * User cannot press button in this state
 */
function setButtonLoadingState () {
    // set to trigger state, add `...` to button text
    $('#button-text').text($('#button-text').text()+'...');
        
    // enable disabled for 2 buttons
    $('#generate-button').attr("disabled", "disabled");
    $('#open-folder-button').attr("disabled", "disabled");
    
    // enable loading spinner
    $("span[id^='loading-status']").each((index, span_ele)=>{
        span_ele.innerHTML = `<span class="spinner-border text-primary spinner-border-sm" id="loading-status-${index}" role="status" aria-hidden="true"></span>`;
    });
}

/**
 * Set status of button back to normal state
 */
function setButtonNormalState () {
    // back to normal state
    $('#button-text').text($('#button-text').text().replace('...',''));

    // enable disabled for 2 buttons
    $('#generate-button').removeAttr('disabled');
    $('#open-folder-button').removeAttr('disabled');

    // disable loading spinner
    $("span[id^='loading-status']").each((index, span_ele)=>{
        span_ele.innerHTML = `<span id="loading-status-${index}"></span>`;
    });

}

/** 
 * Create and run many tasks in sequence
 * @param {dictionary} task_param task configuration with properties:
 * 1) `string` name - Name of task for display on UI
 * 2) `string` method - Method for sending request
 * 3) `Object` {`string`: `Array[str]`}|`null`} request_data - Request data
 * @returns {Promise} `Promise` that resolve `Array` reponse data of all tasks
 */
function run_tasks (task_params) {
    let task_objects = [];
    task_params.forEach((task_param, index)=>{
        task_objects[index] = new Generate(task_params[index]);
    });

    let run_and_get = async (task_objects) => {
        let result_list = [];
        for (task_index in task_objects) {
            const output = await task_objects[task_index].run();
            result_list.push(output);
        }
        return result_list;
    }

    stop_id = setInterval(()=>{
        task_objects.forEach((object, index)=>{
            status_update_panel(object);
            if (index === task_objects.length-1 && task_objects[index].is_done) {
                clearInterval(stop_id);
            }
        });
    }, 200);

    return run_and_get(task_objects);
}


/**
 * @class class for generate, run and update status of tasks
 */
class Generate {
    /** 
     * @param {dictionary} task_param task configuration with properties:
     * 1) `string` name - Name of task for display on UI
     * 2) `string` method - Method for sending request
     * 3) `Object` {`string`: `Array[str]`}|`null`} request_data - Request data
     */
    constructor(task_param) {
        this.task_name = task_param['name'];
        this.request_method = task_param['method'];
        this.request_data = task_param['request_data'];
        this.id_selector = task_param['selector'];
        
        this.is_created = true;
        this.is_execute = false;
        this.is_done = false;
    }
    
    /**
     * @instance run the current task
     * @returns {Promise} data
     */
    run () {
        this.is_execute = true;
        return this.#create_task(this.id_selector, this.request_method, this.request_data)
                .then((response)=>{
                    if (response.ok) {
                        return response.json()
                                .then((data)=>{
                                    this.is_done = true;
                                    this.is_execute = false;
                                    return data
                                })
                    } else {
                        this.is_done = false;
                        return false
                    }
                    
                });
    }

    /**
     * @param {str} task_endpoint
     * @param {str} method
     * @param {dictionary|null} request_data
     * @returns {Promise}
     */
    #create_task (task_endpoint, method, request_data) {
        const tartget_url = `http://127.0.0.1:8000/generate_test_cases/${task_endpoint}`;

        const request_init = {};
        request_init['method'] = method;
        request_init['headers'] = new Headers({
            "Content-Type": "application/json",
        });

        if (request_data !== null) {
            request_init['body'] = JSON.stringify(request_data);
        }
        return fetch(tartget_url,request_init);
    }
    
}

