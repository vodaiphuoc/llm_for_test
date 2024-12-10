function index () {
    console.log('run index in apis.js function');
    let myHeaders = new Headers({
        "Content-Type": "application/json",
    });

    fetch('http://localhost:8000/test', {
        method: 'GET',
        headers: myHeaders
    })
    .then((response)=> {
        if (response.ok) {
            response.text()
            .then((data)=>{
                
                const data_dict = JSON.parse(data);
                $('.test_index_api').text(data_dict['status']);
            })
        }
        
    });
}

