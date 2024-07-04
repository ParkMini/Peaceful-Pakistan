const register = async (username, phone, password, userType) => {
    let path = "/";
    if(userType != "user") {
        path += "register_seller"
    }else {
        path += "register"
    }
    let data = await postRequest(path, {
        username: username,
        phone: phone,
        password: password,
        userType: userType
    })
    data.idx
    location.href = "/success"
}

const login = async (phone, password) => {
    let response = await postRequest("/login", {
        phone: phone,
        password: password
    })

    setUserInfoLocal(response)
    location.href = "/"
}

const setUserInfoLocal = (json) => {
    localStorage.setItem("username", json.user.username)
    localStorage.setItem("userIdx", json.user.idx)
}

const loadUserInfo = async (id) => {
    let data = getRequest(`/users/${id}`)
        .then(response => console.log(response))
    data.idx
    return data;
}

const logout = () => {
    getRequest("/logout")
        .then(response => location.href = "/login")

    localStorage.removeItem("username")
    localStorage.removeItem("userIdx")
}