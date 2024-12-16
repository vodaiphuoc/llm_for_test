/* Define status of generate button and call api to LLM */ 
$('body').ready(()=>{
    $(document).on('click', '#generate-button', function(event){
        setButtonLoadingState();
        
        // check all checkbox
        selected_py_files = [];
        $("input[id$='.py']").each((index, input_ele)=>{
            if (input_ele.checked === true) {
                selected_py_files.push(input_ele.id);
            }
        });

        // then send api to py server
        let myHeaders = new Headers({
            "Content-Type": "application/json",
        });
        fetch('http://127.0.0.1:8000/file_to_test', {
            method: 'POST',
            body: JSON.stringify({
                'file_list': selected_py_files,
            }),
            headers: myHeaders
        })
        .then((response)=>{
            if (response.ok) {
                // suscess create all testcases
                

            } else {
                // show alert cannot create testcases
                
            }
        })
        .catch((error)=>{
            console.log(error);
        });

        // fake process
        setTimeout(()=>{
            console.log('Done processing');
            setButtonNormalState();
            
        }, 3000);
        
    });
});






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
