from fastapi import APIRouter, Request, WebSocket
from starlette.responses import RedirectResponse
from prediction.database.config.db import PlantCollection, EnviCollection
from bson import ObjectId
from prediction.database.schemas.plant import plantEntity, plantsEntity
from prediction.database.schemas.envi import enviEntity, envisEntity
from prediction.database.models.envi import Envi
from prediction.database.APIDrive.drive import deleteInDrive, deleteAllInDrive
from datetime import datetime
router = APIRouter()


# FOR IMAGE

@router.get('/image/one/{id}')
async def image(id):
    return plantEntity(PlantCollection.find_one({"_id": ObjectId(id)}))

@router.get('/images/show/all')
async def images():
   return plantsEntity(PlantCollection.find())

@router.get('/image/delete/{imgID}')
async def delImage(imgID):
    url = f"https://drive.google.com/uc?export=view&id={imgID}"
    PlantCollection.find_one_and_delete({"image_url": url})
    deleteInDrive(imgID)
    return {'message': 'Successfully deleted'}

@router.get("/images/all/delete")
async def delAllImage():
    PlantCollection.delete_many({})
    deleteAllInDrive()
    return {"message ": "All data deleted"}

@router.get("/envis/all/delete")
async def delAllImage():
    EnviCollection.delete_many({})
    return {"message ": "All data deleted"}


