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
const socket = io("/")
socket.on("connect", () => {
    console.log('Websocket connected!')
    console.log(getDate())
    dateEnvi.value = getDate()
    datePredict.value = getDate()
    socket.emit("jsConnect", "js connected")
    socket.emit("date", getDate())
    socket.emit("predict-date", getDate())

})

// IMPLEMENTED

// render username
let dbPassword = "";
socket.on("user", data => {
    username.innerText = data.username
    dbPassword = String(data.password)
    settingUser.innerText = data.username
    adminHandle(data.isAdmin)

})
// get log history
const logsList = $('.last-log__list')
socket.on("logs", logHistory => {
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

// for setting PAGE
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

// Get DATA FOR DATA PAGE
// get envi data
const checkEnvi = $(".check-temp")

checkEnvi.onclick = function (e) {
    tempChart.destroy()
    socket.emit('date', dateEnvi.value)
}

// Listen to required envi result
socket.on("enviResult", data => {
    handleChartData(data)
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
    socket.emit('predict-date', datePredict.value)
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
        fetch('/images/all/delete')
        .then(response => response.json())
        .then(data => alert('Delete successfully'))
        .catch(error => alert(error))
    }
}
const enviDelete = $('.envi-delete__btn')
enviDelete.onclick = function () {
    console.log('deleting')
    let a = confirm('Are you sure to delele?')
    if(a){
        fetch('/envis/all/delete')
            .then(response => response.json())
            .then(data => alert('Delete successfully'))
            .catch(error => alert(error))
    }
}

// FOR CONTROL COMMAND
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
                    socket.emit("predict-date", getDate())
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


