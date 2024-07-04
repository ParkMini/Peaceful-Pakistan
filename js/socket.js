let socket = io(defaultUrl);

socket.on('connect', function() {
    console.log('Connected to server');

    // join 이벤트 전송
    socket.emit('join', { search_record_id: 1 });

});

socket.on('disconnect', function() {
    console.log('Disconnected from server');
});

socket.on('message', function(data) {
    recivedata(JSON.parse(data))
});


const recivedata = (data) => {
    let json = data.json()
    json.name
    json.location
    json.idx
    json.imgUrl
    json.price
}

const createRepairShopConn = (title, message, category, location) => {
    let date = postRequest("socket/create", JSON.stringify({
        title: title,
        message: message,
        category: category,
        location: location
    }));
    socket.socket = connWebSocket(data.getUUID);
}
setTimeout(() => {
    socket.addEventListener("message", (event) => {
        recivedata(event.data)
    })
}, 2000);