const createEstimates = async (repairShopId, searchRecordId, price) => {
    let data = await postRequest("/estimates", {
        repair_shop_id: repairShopId,
        search_record_id: searchRecordId,
        price: price
    })

    data.idx
}

const selectEstimates = async (searchRecordId, estimateId) => {
    let data = await postRequest("/select_estimate", {
        search_record_id: searchRecordId,
        estimate_id: estimateId
    })

    data.idx
}