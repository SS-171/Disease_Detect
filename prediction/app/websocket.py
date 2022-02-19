from prediction.database.config.db import UserCollection, LogCollection,EnviCollection, PlantCollection
from datetime import datetime
import prediction.app.authenticate as auth

onlineUsers = []
camPos = 0
pumpPos = 0 
def getLogTime():
    now = datetime.now()
    nowStr = now.strftime("%d/%m/%y %H:%M:%S")
    return nowStr
def getEnviTime():
    now = datetime.now()
    nowStr = now.strftime("%Y-%m-%d %H:%M:%S")
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
def saveEnvi(temp, humid):
    now = getEnviTime().split(" ")
    EnviCollection.insert_one({
        "temp": temp,
        "humid": humid,
        "dateCreated" : now[0],
        "timeCreated": now[1]
    })
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
        saveLogToDb(username)
        hisLog = getLog(username)
        user.pop("_id", None)
        await sio.emit("user", {"password": user["password"], "isAdmin": user["isAdmin"], "sid": sid})
        await sio.emit("users", {"userList":getUsers(), "onlineUsers": onlineUsers})
        await sio.emit("logs", hisLog)
        await sio.emit("camPos1",  {"pos": camPos, "sid": 0})
        await sio.emit("pumpPos1", {"pos": pumpPos, "sid": 0})


    @sio.on("control")
    async def control(sid, msg):
        await sio.emit("control", msg)

    # Temp and Humid handle

    # transfer envi from ras to js
    @sio.on("envi")
    async def envi(sid, msg):
        saveEnvi(msg['temp'], msg['humid'])
        await sio.emit('envi', msg)

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
    @sio.on("disconnect")
    async def disconnect(sid):
        removeOnlineUser(sid)
        print("on disconnect")