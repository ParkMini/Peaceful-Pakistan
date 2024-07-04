const aiSearch = async () => {
    let form = document.getElementById('aiSearchForm')
    
    const formData = new FormData(form);
    
    let data = await postFormRequest('/search_records', formData)
        .then(response => response.json())
    data[0]
}


