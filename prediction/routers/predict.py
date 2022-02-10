from fastapi import APIRouter, File, UploadFile
from ..Img_process.classify import read_image, predict, preprocess1, extract_features
from ..Img_process.segmentation import predict_segment
router = APIRouter()

@router.post('/disease/predict/not_seg')
async def predict_not_seg(file: bytes = File(...)):
    extension = file.filename.split(".")[-1] in ("JPG","jpg", "jpeg", "JPEG", "png", "PNG")
    if not extension:
        return "Image must be jpg or png format!"
    image = read_image(await file.read())
    image = preprocess1(image)
    features = extract_features(image)
    result = predict(features)
    return result

@router.post('/disease/predict')
async def predict_seg(file: UploadFile = File(...)):
    extension = file.filename.split(".")[-1] in ("JPG","jpg", "jpeg", "JPEG", "png", "PNG")
    if not extension:
        return "Image must be jpg or png format!"
    image = read_image(await file.read())
    # predict
    result = predict_segment(image)
    return result

