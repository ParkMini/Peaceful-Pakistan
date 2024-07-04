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
    let data = await postRequest("https://api.odcloud.kr/api/nts-businessman/v1/validate?serviceKey=%2BcetiQrNvXBv7SbdBJHa6%2BofRXmOPrTzF1N6eRUFslkPd1g%2FjFZLRQfqKyUggaXbUR%2FjuU%2BAyQ9UnxHADV56Bw%3D%3D", {
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
    console.log(data)
    data.data
}

const checkRepairShopA = () => {
    let json = {
        "request_cnt": 1,
        "status_code": "OK",
        "data": [
            {
                "b_no": "0000000000",
                "valid": "02",
                "valid_msg": "확인할 수 없습니다.",
                "request_param": {
                    "b_no": "0000000000",
                    "start_dt": "20000101",
                    "p_nm": "홍길동",
                    "p_nm2": "홍길동",
                    "b_nm": "(주)테스트",
                    "corp_no": "0000000000000",
                    "b_type": "",
                    "b_sector": "",
                    "b_adr": ""
                }
            }
        ]
    }

    location.href = "/repair_shops/add"
}

const createRepairShop = async () => {
    let form = document.getElementById("repairShopForm");

    let formData = new FormData(form)
    let data = await postRequest("/repair_shops", {
        "name": formData.get("name"),
        "location": formData.get("location"),
        "category_id": formData.get("categorys"),
        "description": formData.get("description"),
        "phone_number": formData.get("phoneNumber"),
        "owner_id": localStorage.getItem("userIdx")
    })
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