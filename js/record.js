const getRecords = async () => {
    let data = await getRequest("/search_records")

    data[0]
}

const getRecordById = async (id) => {
    let data = await getRequest(`/search_records/${id}`)
    data.idx
}