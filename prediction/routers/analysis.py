from fastapi import APIRouter, Request, WebSocket

from prediction.database.ImgHandle import collection
from bson import ObjectId
from prediction.database.schemas.plant import plantEntity, plantsEntity
from PIL import Image
import io
router = APIRouter()


@router.get('/image/{id}')
async def image(id):
    return plantEntity(collection.find_one({"_id": ObjectId(id)}))

@router.get('/images')
async def images():
   return plantsEntity(collection.find())
    # return pil_imgs