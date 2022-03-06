from fastapi import APIRouter, File, UploadFile
from ..Img_process.classify import read_image, predict,  extract_features
from ..Img_process.segmentation import predict_segment
router = APIRouter()

@router.post('/disease/predict')
async def predict_seg(file: UploadFile = File(...)):
    extension = file.filename.split(".")[-1] in ("JPG","jpg", "jpeg", "JPEG", "png", "PNG")
    if not extension:
        return "Image must be jpg or png format!"
    image = read_image(await file.read())
    # predict
    result = predict_segment(image)
    return result

