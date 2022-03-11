from prediction.database.config.db import UserCollection, LogCollection,EnviCollection, PlantCollection
from datetime import datetime

onlineUsers = []
camPos = 0
pumpPos = 0 
height = 0
def getLogTime():
    now = datetime.now()
    nowStr = now.strftime("%d/%m/%y %H:%M:%S")
    return nowStr


def saveLogToDb(username):
    LogCollection.insert_one({"username": username,"time":getLogTime() })

def getLog(username):
    logHis = LogCollection.find({"username":username}, {"_id": 0, "time": 1}).limit(3).sort([('$natural',-1)])
    list_log = list(logHis)
    return list_log

def filterData(collection,chosenDate):
    data = collection.find({"dateCreated": chosenDate},{"_id": 0, "dateCreated": 0})
    return data

def saveOnlineUser(sid, username):
    user = {"sid": sid, "username": username}
    global onlineUsers
    if not user in onlineUsers:
        onlineUsers.append(user)
    else:
        onlineUsers[user]['sid'] = sid
def removeOnlineUser(sid):
    for each in onlineUsers:
        if(each['sid'] == sid):
            onlineUsers.remove(each)
            break
def getUsers():
    return (list(UserCollection.find({}, {"_id":0})))
def websocket(sio, socket_app, app):
    @app.get("/update/envi/")
    async def getEnvi(temp: int, humid: int):
        saveEnvi(temp, humid)
        await sio.emit('sameDate', {"date": datetime.now().strftime("%Y-%m-%d")})
        return {"msg":"post created"}

    def saveEnvi(temp, humid):
        now = getEnviTime().split(" ")
        EnviCollection.insert_one({
            "temp": temp,
            "humid": humid,
            "dateCreated" : now[0],
            "timeCreated": now[1]
        })

    def getEnviTime():
        now = datetime.now()
        nowStr = now.strftime("%Y-%m-%d %H:%M:%S")
        return nowStr

    app.mount("/", socket_app)  # Here we mount socket app to main fastapi app

    @sio.on("connect")
    async def connect(sid, env):
        print("Client on connect")

    # implementedd + delete All logs


    @sio.on("jsConnect")
    async def jsConnect(sid, username):
        user = UserCollection.find_one({"username": username})
        saveOnlineUser(sid, username)
        # save log history with time and date
        hisLog = getLog(username)
        user.pop("_id", None)
        await sio.emit("user", {"password": user["password"], "isAdmin": user["isAdmin"], "sid": sid})
        await sio.emit("users", {"userList":getUsers(), "onlineUsers": onlineUsers})
        await sio.emit("logs", {"logs":hisLog, "username": username})
        await sio.emit("camPos2",  {"pos": camPos, "sid": 0})
        await sio.emit("pumpPos2", {"pos": pumpPos, "sid": 0})
        await sio.emit("height2", height)

    @sio.on("control")
    async def control(sid, msg):
        await sio.emit("control", msg)

    # Filter data by date


    @sio.on("date")
    async def getdate(sid, data):
        data = list(filterData(EnviCollection,data['date']))
        await sio.emit("enviResult", data)
    @sio.on('predict-date')
    async def getPredict(sid, data):
        data = list(filterData(PlantCollection,data['date']))
        await sio.emit("predictResult", data)

    @sio.on("camPos")
    async def camPosition(sid, data):
        print("cam position:", data)
        global camPos
        camPos = data['pulse']
        data['sid'] = sid
        await sio.emit("camPos1", data)

    @sio.on("pumpPos")
    async def pumpPosition(sid, data):
        print("pump position:", data)
        global pumpPos
        pumpPos = data['pulse']
        data['sid'] = sid
        await sio.emit("pumpPos1", data)

    @sio.on("height")
    async def heightFcn(sid, data):
        global height
        height = data
        await sio.emit("height1", data)
    @sio.on("rasPredict")
    async def rasPredict(sid, data):
        await sio.emit("rasPredict", data)
    @sio.on("rasPredictResult")
    async def rasPredict(sid, data):
        await sio.emit("rasPredictResult", data)
    @sio.on("runPump")
    async def runPump(sid, data):
        await sio.emit("runPump", data)
    @sio.on("reset")
    async def reset(sid, data):
        global camPos, pumpPos
        camPos = 0
        pumpPos = 0
        await sio.emit("camPos2",  {"pos": camPos, "sid": 0})
        await sio.emit("pumpPos2", {"pos": pumpPos, "sid": 0})
        await sio.emit("reset", 1)
    @sio.on("rasConnect")
    async def rasConnect(sid, data):
        if(data):
            await sio.emit("rasConnect",1)
    @sio.on("disconnect")
    async def disconnect(sid):
        removeOnlineUser(sid)
        print("on disconnect")