const getRecords = async () => {
    let data = await getRequest("/search_records")

    data[0]
}

const getRecordById = async (id) => {
    let data = await getRequest(`/search_records/${id}`)
    data.idx
}

const createRecord = async () => {
    let form = document.getElementById("recordForm")
    let formData = new FormData(form)

    let data = await postFormRequest("/search_records", formData)

}