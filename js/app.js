const defaultUrl = "http://172.30.1.86:5000";

const showErrorModel = (message) => {
    alert(message);
    throw new Error(message || "알수 없는 에러가 발생하였습니다.")
}

const getRequest = async (path) => {
    return fetch(defaultUrl + path, {
        headers: {
            "Access-Control-Expose-Headers": "Location",
            "Access-Control-Allow-Credentials": true
        },
        credentials: 'include'
    })
    .then(response => {
        if(!response.ok) {
            return response.json().then(data => {
                showErrorModel(data.message || "알수 없는 에러가 발생하였습니다.");
                // throw new Error(data.message || "Unknown error occurred");
            });
        }
        return response.json(); // 응답 데이터를 JSON으로 파싱
    })
}

const postRequest = async (path, body) => {
    let error = false
    return fetch(defaultUrl + path, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Access-Control-Expose-Headers": "Location",
            "Access-Control-Allow-Credentials": true
        },
        credentials: 'include',
        body: JSON.stringify(body) // body를 JSON 문자열로 변환
    })
    .then(response =>  {
        if(!response.ok) {
            return response.json().then(data => {
                showErrorModel(data.message);
                error = true
                // throw new Error(data.message || "Unknown error occurred");
            });
        }
        return response.json(); // 응답 데이터를 JSON으로 파싱
    })
    .catch(err => {
        if(err == false)
            showErrorModel("알수 없는 에러가 발생하였습니다.")
    })
}

const postApiRequest = async (url, body) => {
    let error = false
    return fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Access-Control-Expose-Headers": "Location",
            "Access-Control-Allow-Credentials": true
        },
        credentials: 'include',
        body: JSON.stringify(body) // body를 JSON 문자열로 변환
    })
    .then(response =>  {
        if(!response.ok) {
            return response.json().then(data => {
                showErrorModel(data.message);
                error = true
                // throw new Error(data.message || "Unknown error occurred");
            });
        }
        return response.json(); // 응답 데이터를 JSON으로 파싱
    })
    .catch(err => {
        if(err == false)
            showErrorModel("알수 없는 에러가 발생하였습니다.")
    })
}

const postFormRequest = async (path, body) => {
    let error = false
    return fetch(defaultUrl + path, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "Access-Control-Expose-Headers": "Location",
            "Access-Control-Allow-Credentials": true
        },
        credentials: 'include',
        body: JSON.stringify(body) // body를 JSON 문자열로 변환
    })
    .then(response =>  {
        if(!response.ok) {
            return response.json().then(data => {
                showErrorModel(data.message);
                error = true
                // throw new Error(data.message || "Unknown error occurred");
            });
        }
        return response.json(); // 응답 데이터를 JSON으로 파싱
    })
    .catch(err => {
        if(err == false)
            showErrorModel("알수 없는 에러가 발생하였습니다.")
    })
}

const categorySearch = () => {
    getRequest("/category/get")
        .then(data => {
            console.log(data);
            // 응답 데이터를 사용하여 필요한 작업 수행
        })
        .catch(err => {
            console.error('Error:', err);
            // 에러 이후 처리 코드 작성
        });
}

const createCategory = async (name) => {
    let data = await postRequest("/categories", {
        name: name
    })
    data.idx
    alert("등록 성공")
}

// categorySearch 함수 호출
// categorySearch();
