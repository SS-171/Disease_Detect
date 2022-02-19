from fastapi import APIRouter, Request, WebSocket
from starlette.responses import RedirectResponse
from prediction.database.config.db import PlantCollection, EnviCollection, UserCollection
from bson import ObjectId
from prediction.database.schemas.plant import plantEntity, plantsEntity
from prediction.database.schemas.envi import enviEntity, envisEntity
from prediction.database.models.envi import Envi
from prediction.database.APIDrive.drive import  deleteDateDriveData
from datetime import datetime
router = APIRouter()


# FOR IMAGE
def getImageIdList(date):
    ids = []
    items = list(PlantCollection.find({"dateCreated":date},{"_id":0, "image_id":1}))
    for x in items:
        ids.append(x.get("image_id"))
    return ids

@router.get("/images/date/delete/{date}")
async def delImage(date: str):
    items = getImageIdList(date)
    deleteDateDriveData(items)
    PlantCollection.delete_many({"dateCreated": date})
    return {"message ": "Data deleted"}

@router.get("/envis/date/delete/{date}")
async def delImage1(date: str):
    EnviCollection.delete_many({"dateCreated": date})
    return {"message ": "Data deleted"}

@router.get("/users/all")
async def getUsers():
    users = UserCollection.find({}, {"_id": 0,"password":0})
    return list(users)

