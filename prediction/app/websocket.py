from prediction.database.config.db import UserCollection, LogCollection,EnviCollection, PlantCollection
from datetime import datetime
import prediction.app.authenticate as auth
def getLogTime():
    now = datetime.now()
    nowStr = now.strftime("%d/%m/%y %H:%M:%S")
    return nowStr
def getEnviTime():
    now = datetime.now()
    nowStr = now.strftime("%Y-%m-%d %H:%M:%S")
    return nowStr

def saveLogToDb():
    LogCollection.insert_one({"time":getLogTime()})

def getLog():
    logHis = LogCollection.find({}, {"_id": 0, "time": 1}).limit(3).sort([('$natural',-1)])
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

def websocket(sio, socket_app, app):

    app.mount("/", socket_app)  # Here we mount socket app to main fastapi app

    @sio.on("connect")
    async def connect(sid, env):
        print("Client on connect")

    # implementedd + delete All logs


    @sio.on("jsConnect")
    async def jsConnect(sid, msg):
        print(msg)
        user = UserCollection.find_one({"username": auth.currentUser})
        # save log history with time and date
        saveLogToDb()
        hisLog = getLog()
        user.pop("_id", None)
        await sio.emit("user", user)
        await sio.emit("logs", hisLog)


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
    async def getdate(sid, chosenDate):
        data = list(filterData(EnviCollection,chosenDate))
        await sio.emit("enviResult", data)
    @sio.on('predict-date')
    async def getPredict(sid, chosenDate):
        data = list(filterData(PlantCollection,chosenDate))
        await sio.emit("predictResult", data)

    @sio.on("disconnect")
    async def disconnect(sid):
        print("on disconnect")