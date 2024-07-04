// const getRepairShops = (category) => {
//     getRequest(`/repairShop/get?category=${category}`)
//         .then(response => response.json())
// }

const getRepairShop = async (id) => {
    let data = await getRequest(`/repairShop/${id}`)
        .then(response => response.json())
    
    data.idx
}

const checkRepairShop = async (b_no, start_dt, p_nm) => {
    postRequest("https://api.odcloud.kr/api/nts-businessman/v1/validate?serviceKey=%2BcetiQrNvXBv7SbdBJHa6%2BofRXmOPrTzF1N6eRUFslkPd1g%2FjFZLRQfqKyUggaXbUR%2FjuU%2BAyQ9UnxHADV56Bw%3D%3D", {
        businesses: [
            {
                b_no: b_no,
                start_dt: start_dt,
                p_nm: p_nm,
                p_nm2: "",
                b_nm: "",
                corp_no: "",
                b_sector: "",
                b_type: "",
                b_adr: ""
            }
        ]
    })
}

const createRepairShop = async () => {
    let form = document.getElementById("repairShopForm");

    let formData = new FormData(form)
    let data = await postRequest("/repair_shops", formData)
    .then(response => response.json())
    data.idx
}

// const getReview =  async(id) => {
//     let data = getRequest(`/review/get/${id}`)
//     data.score
// }

const createReview = async (id, content) => {
    postRequest('/reviews', {
        user_id: id,
        content: content,
        score: score,
        user_id: localStorage.getItem("userIdx")
    })
    .then(response => location.reload)

}

const getRepairShopByCategory = async (id) => {
    let data = await getRequest(`/category/${id}/repair_shops`)
    data[0]
}