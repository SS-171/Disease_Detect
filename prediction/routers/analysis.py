from fastapi import APIRouter, Request, WebSocket

from prediction.database.config.db import PlantCollection, EnviCollection
from bson import ObjectId
from prediction.database.schemas.plant import plantEntity, plantsEntity
from prediction.database.schemas.envi import enviEntity, envisEntity
from prediction.database.models.envi import Envi
from datetime import datetime
router = APIRouter()



@router.get('/image/{srcID}')
async def image(srcID):
    return plantsEntity(PlantCollection.find({"srcID": srcID}))

@router.get('/image/one/{id}')
async def image(id):
    return plantEntity(PlantCollection.find_one({"_id": ObjectId(id)}))

@router.get('/images/all')
async def images():
   return plantsEntity(PlantCollection.find())
    # return pil_imgs

# Post environment parameter to server and save to db
@router.post('/environment/post')
async def envi(envi):
    envi = dict(Envi(
        temp = envi.temp,
        humid = envi.humid,
        time = datetime.now()
    ))
    EnviCollection.insert_one(envi)

# Get envi prm from db
@router.get('/environment/get/{time}')
async def envi(time: str):
    if(time == 'day'):
        envisEntity()
