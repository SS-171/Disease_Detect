// for expand arrow

var $ = document.querySelector.bind(document);
var $$ = document.querySelectorAll.bind(document);
const expandArrow = $('.expand-arrow');
const graphList = $('.graph-list');
const contentItems = $$('.menu .content__item');
const dataList = $('.data-menu__list');
const dataListBtn = $('.data-menu__icon');
const overlayImg = $('.overlay__img');
const overlay = $('.overlay');
const diseaseMenuItems = $$(".graph__item a");
const camSlider = $('.cam-slider')
const pumpSlider = $(".pump-slider")
const username = $('.user__name')
const tempCtx = $('#tempChart');
let dateEnvi = $('.date-envi')
let datePredict = $('.date-predict')
let settingUser = $("#setting .user__name")
let tempChart;
// render chart
function renderChart(tempData, humidData) {
    // 
    const Data = {
        datasets: [{
            label: 'Temprature',
            backgroundColor:
                [
                    'rgb(242, 13, 13)',

                ],
            borderColor: [
                '#000',

            ],
            // data: [{ x: '2016-12-25', y: 20 }, { x: '2016-12-26', y: 15 }, { x: '2016-12-27', y: 30 }, { x: '2016-12-28', y: 28 }, { x: '2016-12-29', y: 35 }],
            data: tempData,
            borderWidth: 2,
            borderColor: 'rgb(242, 13, 13)'
        },
        {
            label: 'Humidity',
            backgroundColor:
                [
                    'rgb(11, 142, 11)',

                ],
            borderColor: [
                '#000',

            ],
            data: humidData,
            borderWidth: 2,
            borderColor: 'rgb(11, 142, 11)'
        }
        ]
    };

    const tempConfig = {
        type: 'line',
        data: Data,

        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#ccc' }
                },
                x: {
                    grid: { color: '#ccc' }
                }
            },
            responsive: true,
            maintainAspectRatio: false,
        }
    };
    tempChart = new Chart(tempCtx, tempConfig);

}

// for data page
function toggleDataMenu() {
    dataList.classList.toggle("data-menu--show");
}

overlayImg.onclick = function (e) {
    e.stopPropagation();
}
window.addEventListener('click', function () {
    overlay.classList.remove('overlay--show');
})
// show scroll up
function scrollUp() {
    const scrollBtn = document.getElementById('scroll-up');
    if (this.scrollY >= 100) scrollBtn.classList.add('scroll--show');
    else scrollBtn.classList.remove('scroll--show');
}
window.addEventListener("scroll", scrollUp);
// for panel
expandArrow.onclick = function () {
    expandArrow.classList.toggle('expand-arrow--down')
    graphList.classList.toggle('graph-list--show')
}
function disappearContent() {
    $$('.content .content__item').forEach(item => {
        item.classList.remove('content--show')
    })
}

contentItems.forEach(function (each) {
    each.addEventListener('click', function (e) {
        parent = e.target.parentNode
        parent.focus()
        disappearContent()
        const element = each.href.split("#", -1)[1];
        $(`.content #${element}`).classList.toggle('content--show');

    })
})

// show disease in from menu list
diseaseMenuItems.forEach(each => {
    each.onclick = () => {
        disappearContent();
        $(".content #blog").classList.add('content--show')
    }
})

// FOR DASHBOARD



// FOR BLOG
const blogSwiper = new Swiper('.blog__swiper', {
    // Optional parameters
    spaceBetween: 16,
    centeredSlides: true,
    loop: true,
    slidesPerView: "auto",
    // If we need pagination
    pagination: {
        el: '.swiper-pagination',

        clickable: true,
    },

    // Navigation arrows
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },

});




// WEBSOCKET
let cookie = document.cookie
let usernameText = cookie.split('=').pop()
username.innerText = usernameText
settingUser.innerText = usernameText
const socket = io("/")
socket.on("connect", () => {
    console.log('Websocket connected!')
    dateEnvi.value = getDate()
    datePredict.value = getDate()
    socket.emit("jsConnect", usernameText)
    socket.emit("date", { date: getDate() })
    socket.emit("predict-date", { date: getDate()})

})

// IMPLEMENTED

// render username
let dbPassword = "";
let isAdmin = false
socket.on("user", user => {
    if (user.sid == socket.id) {
        dbPassword = String(user.password)
        isAdmin = Boolean(user.isAdmin)
        adminHandle(user.isAdmin)
    }

})
// get log history
const logsList = $('.last-log__list')
socket.on("logs", data => {
    let logHistory = data.logs
    let name = data.username
    if(name == usernameText){

        let htmls = logHistory.map(each => {
            let datetime = String(each.time).split(" ")
            let date = datetime[0]
            let time = datetime[1]
    
            let listItem = `
                <li class="last-log__item">
                    <p class="last-log__time">${date} at ${time}</p>
                </li>
            `
            return listItem
        })
        logsList.innerHTML = htmls.join("");
    }

})



// listen temp and humid 
const currentTemp = $(".current-temp")
const currentHumid = $('.current-humid')
socket.on("envi", data => {
    console.log("temp", data.temp)
    console.log("humid", data.humid)
    currentTemp.innerText = `${data.temp}°C`
    currentHumid.innerText = `${data.humid}%`
})

// SETTING PAGE
// 
let userTable = $('.user-table')
let onlineUsers = []
let userList = []
socket.on("users", users => {
    userTable.innerHTML = `
        <tr>
            <th>#</th>
            <th>Name</th>
            <th>Date created</th>
            <th>Role</th>
            <th>Status</th>
            <th>Action</th>
        </tr>
    `
    onlineUsers = users.onlineUsers
    userList = users.userList
    userListHandle(users.userList)
    console.log("online",onlineUsers)
})
// validate user create
const updateUsername = $(".update-info.admin input[name='username']")
const updateInfoBtn = $(".update-info__btn.create-user")
updateInfoBtn.onclick = function (e) {
    console.log("click")
    let isSame = false
    userList.map(each => {
        if (each.username == updateUsername.value) {
            isSame = true
        }
    })
    if (isSame) {
        e.preventDefault()
        alert('This username has already existed. Try another one.')
    }

}
// update username and password
const currentPassword = $('.current-password')
const newPassword = $('.newpassword')
const confirmPwd = $('.confirm-newpassword')
const submitNewPwd = $('.submit-newpassword')

submitNewPwd.onclick = function (e) {
    if ((newPassword.value !== confirmPwd.value)) {
        e.preventDefault();
        alert('Your password does not match. Please try again.')
    }
    if (String(currentPassword.value) !== dbPassword) {
        console.log(String(currentPassword))
        e.preventDefault();
        alert('Your current password was wrong. Please try again.')
    }
}
function checkOnline(username) {
    let isOnline = false
    onlineUsers.forEach(each => {
        if(each.username === username) {
            isOnline = true
        }
    })
    return isOnline
}
function userListHandle(users) {
    users.map((each, index) => {
        let isOnline = checkOnline(each.username)
        console.log("name", each.username, "isOnline", isOnline)
        let row = userTable.insertRow(index + 1)
        let cell1 = row.insertCell(0)
        let cell2 = row.insertCell(1)
        let cell3 = row.insertCell(2)
        let cell4 = row.insertCell(3)
        let cell5 = row.insertCell(4)
        let cell6 = row.insertCell(5)
        cell1.innerHTML = index + 1
        cell2.innerHTML = each.username
        cell3.innerHTML = each.dateCreated
        cell4.innerHTML = `
            <p class="user-list__text">${each.isAdmin ? "Admin" : "User"}</p>
        `
        cell5.innerHTML = `
            <div class="flex-userlist">
                <div id="user-number-${index + 1}" class="online-icon"></div>
                <p class="user-list__text">${isOnline ? "Online" : "Offline"}</p>
            </div>
        `
        if (isAdmin) {
            if(!each.isAdmin)
            cell6.innerHTML = `
                <a href="/admin/delete/user/?username=${each.username}" class="delete-user">
                    <i class="bx bxs-x-circle"></i>
                </a>
            `
        }
        if (isOnline) {
            $(`#user-number-${index+ 1}`).classList.add("online-icon--online")
        }

    })
}


// Get DATA FOR DATA PAGE
// get envi data
const checkEnvi = $(".check-temp")

checkEnvi.onclick = function (e) {
    tempChart.destroy()
    socket.emit('date', {date: dateEnvi.value})
}

// Listen to required envi result
socket.on("enviResult", data => {
    
    handleChartData(data)
})

socket.on("sameDate", data=>{
    if(data.date == dateEnvi.value){
        tempChart.destroy()
        socket.emit("date", { date: getDate() })
    }
})

//GET PREDICT DATA TABLE
function showDetail(){
    disappearContent();
    $(".content #blog").classList.add('content--show')

}
function showDiseaseImage(){
    event.stopPropagation()
    const imgUrl = event.target.getAttribute("url")
    overlayImg.setAttribute("src", imgUrl)
    overlay.classList.add('overlay--show')
}

// 
const checkPredict = $(".check-predict")
const imageTable = $('.img-table')
let htmlRows = '';
let headerTable = `
    <tr>
        <th>Kết quả dự đoán</th>
        <th>Thời gian</th>
        <th>Chi tiết bệnh</th>
        <th>Hình ảnh</th>
    </tr>
`
checkPredict.onclick = function () {
    socket.emit('predict-date', {date:datePredict.value})
}
socket.on("predictResult",function (data){
    
    let html = data.map((each, index)=>{
        let htmlContent = 
        `
        <tr>
            <td>${each.status}</td>
            <td>${each.timeCreated}</td>
            <td>
                <a href="#${each.status}" class="data-disease__detail" onclick=showDetail()>Xem chi tiết</a>
            </td>
            <td>
                <p url="${each.image_url}" class="img-show" onclick=showDiseaseImage() >Xem ảnh</p>
            </td>
        </tr>
        `
        return htmlContent
    })
    htmlRows = html.join("")
    let htmlTable = headerTable.concat(htmlRows)
    imageTable.innerHTML = htmlTable
    
    
})
// DELETE USER DATA
const predictDelete = $('.predict-delete__btn')
predictDelete.onclick = function(){
    let a= confirm('Are you sure to delele?')
    if(a){
        fetch(`/images/date/delete/${datePredict.value}`)
        .then(response => response.json())
        .then(data => {
            socket.emit("predict-date", { date: datePredict.value})
            alert('Delete successfully')
        })
        .catch(error => alert(error))
    }
}
const enviDelete = $('.envi-delete__btn')
enviDelete.onclick = function () {
    
    let a = confirm('Are you sure to delele?')
    if(a){
        fetch(`/envis/date/delete/${dateEnvi.value}`)
            .then(response => response.json())
            .then(data => {
                socket.emit("date", { date: dateEnvi.value })
                tempChart.destroy()
                alert('Delete successfully')
            })
            .catch(error => alert(error))
    }
}

// FOR DASHBOBARD
const turnLeft = $(".btn.btn__left")
const turnRight = $(".btn.btn__right")
const forward = $(".btn.btn__up")
const backward = $(".btn.btn__down")
const stopCmd = $(".btn.btn__stop")

turnLeft.onclick = () => {
    socket.emit("control", "left")
}
turnRight.onclick = () => {
    socket.emit("control", "right")
}
forward.onclick = () => {
    socket.emit("control", "forward")
}
backward.onclick = () => {
    socket.emit("control", "backward")
}
stopCmd.onclick = () => {
    socket.emit("control", "stop")
}

// Camera and pump position update
let currentCamPos = 0
let currentPumpPos = 0
socket.on("camPos2", data => {
    if (data.sid !== socket.id) {
        camSlider.value = data.pos
        currentCamPos = camSlider.value
    }
})
socket.on("pumpPos2", data => {
    if (data.sid !== socket.id) {
        pumpSlider.value = data.pos
        currentPumpPos = pumpSlider.value
    }
})

camSlider.onchange = function () {
    let direct;
    nowCamPos = Number(camSlider.value)
    if (nowCamPos > currentCamPos) {
        direct = 0
        pulse = nowCamPos - currentCamPos
    }
    else {
        direct = 1
        pulse = currentCamPos - nowCamPos
    }
    currentCamPos = nowCamPos

    socket.emit('camPos', { direct: direct, pulse: pulse, pos: currentCamPos })
}
pumpSlider.onchange = function () {
    let direct;
    nowPumpPos = Number(pumpSlider.value)
    if (nowPumpPos > currentPumpPos) {
        direct = 0
        pulse = nowPumpPos - currentPumpPos
    }
    else {
        direct = 1
        pulse = currentPumpPos - nowPumpPos
    }
    currentPumpPos = nowPumpPos
    socket.emit('pumpPos', { direct: direct, pulse: pulse, pos: currentPumpPos })
}

//FOR ADMIN HANDLE
const adminText = $('.admin__text')
const userCreate = $('.update-info.admin')
const userAvatar = $('.user__avatar')
const settingUserAvt = $(".setting-right__image")
function adminHandle(isAdmin) {
    if (isAdmin) {
        userCreate.style.display = "flex"
        $$('.update-info__input.new').forEach(e => {
            e.value = ""
        })
        userAvatar.setAttribute("src", "/prediction/static/img/admin.jpeg")
        settingUserAvt.setAttribute("src", "/prediction/static/img/admin.jpeg")
        // get all user
        fetch("/users/all")
        .then(response => response.json())
        .then(data => console.log("user list", data))
    }
    else {
        userCreate.style.display = "none"
        userAvatar.setAttribute("src", "/prediction/static/img/user.png")
        settingUserAvt.setAttribute("src", "/prediction/static/img/user.png")
    }
}


// FOR PREDICTION
const form = $('.dashboard__predict')
const inputImg = $('.input__img')
const submitBtn = $(".predict-img__btn")
const predictResult = $(".img__show")
let htmlResult ="";
submitBtn.onclick = function (e) {
    console.log("submit")
    if(inputImg.value){
        htmlResult =""
        predictResult.innerHTML = `
        <p class="predicting__status"> Predicting...</p>
        `
        e.preventDefault();
        let data = new FormData()
        data.append('file', inputImg.files[0])
        fetchImage(data)
            .then(result => {
                if (typeof(result) === "string") {
                    console.log(result)
                    htmlResult = `
                         <p class="predict-result__text">Not found any leaf in image</p>
                        `
                }
                else {
                    Object.keys(result).forEach(each => {
                        console.log(each)
                        console.log("status", result[each].status)
                        console.log("url-img", result[each].url)
                        let html= `
                            <div class="predict__result">
                                <img src="${result[each].url}" alt="" class="predict__img">
                                <p class="predict-result__text">${result[each].status}</p>
                            </div>
                        `
                        htmlResult = htmlResult.concat(html)
    
                    })
                    
                }
            })
            .then(result=>{
                predictResult.innerHTML = htmlResult
                if (datePredict.value == getDate()){
                    socket.emit('predict-date', { date: datePredict.value })

                }

            })
    }
    else alert("You ain't chosen an image yet")
}
async function fetchImage(data){
    let response = await fetch("/disease/predict",{
        method: "POST",
       
        body: data
    })
    return response.json()
}
// Height input
const heightInput = $('.height__input')
const submitHeightBtn = $('.height-submit')
submitHeightBtn.onclick = function () {
    if (isNaN(heightInput.value) || heightInput.value.length == 0 || heightInput.value > 60) {

        alert("Invalid height input. Try again!")
        heightInput.value = ''
    }
    else {
        socket.emit("height", heightInput.value)
    }
}
socket.on("height2", height => {
    heightInput.value = height
})

//Sub function
function handleChartData(data) {
    let tempData = new Array()
    let humidData = new Array()
    data.forEach(each => {
        tempData.push({
            x: each.timeCreated,
            y: each.temp
        })
        humidData.push({
            x: each.timeCreated,
            y: each.humid
        })
    })
    renderChart(tempData, humidData)
}
function getDate() {
    const d = new Date()
    month = d.getMonth() < 10 ? '0' + (d.getMonth() + 1) : d.getMonth()
    day = d.getDate() < 10 ? '0' + d.getDate() : d.getDate()
    let date = `${d.getFullYear()}-${month}-${day}`
    return date
}

window.onbeforeunload = function () {
    document.cookie = `username = ${usernameText}`
    return confirm("confirm refresh")
}