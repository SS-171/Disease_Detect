from fastapi import APIRouter, Request, WebSocket

from prediction.database.config.db import PlantCollection, EnviCollection
from bson import ObjectId
from prediction.database.schemas.plant import plantEntity, plantsEntity
from prediction.database.schemas.envi import enviEntity, envisEntity
from prediction.database.models.envi import Envi
from prediction.database.APIDrive.drive import deleteInDrive
from datetime import datetime
router = APIRouter()


# FOR IMAGE
@router.get('/image/{srcID}')
async def image(srcID):
    return plantsEntity(PlantCollection.find({"srcID": srcID}))

@router.get('/image/one/{id}')
async def image(id):
    return plantEntity(PlantCollection.find_one({"_id": ObjectId(id)}))

@router.get('/images/all')
async def images():
   return plantsEntity(PlantCollection.find())

@router.get('/image/delete/{imgID}')
async def delImage(imgID):
    url = f"https://drive.google.com/uc?export=view&id={imgID}"
    PlantCollection.find_one_and_delete({"image_url": url})
    deleteInDrive(imgID)
    return {'message': 'Successfully deleted'}


# Get envi prm from db
@router.get('/environment/get/{time}')
async def envi(time: str):
    if(time == 'day'):
        envisEntity()
