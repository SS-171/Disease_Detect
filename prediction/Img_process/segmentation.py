# python -m venv myEnv
# myEnv
import cv2 as cv
import numpy as np
import os 
from datetime import datetime
from ..database.config.db import PlantCollection
from ..database.APIDrive.drive import saveToDrive
from PIL import Image
import random
MODEL_DIR = "prediction/Img_process/resource/model5.h5"
from .source import get_mask_contours, load_inference_model
from .classify import  preprocess,extract_features, predict
num_classes = 1
model, inference_config = load_inference_model(num_classes, MODEL_DIR)
def getPredictTime():
    now = datetime.now()
    nowStr = now.strftime("%Y-%m-%d %H:%M:%S")
    return nowStr
def savePredictResult(url, status, img_id):
    now = getPredictTime().split(" ")
    PlantCollection.insert_one({
        "image_id": img_id,
        "image_url": url,
        "status": status,
        "dateCreated" : now[0],
        "timeCreated": now[1]
    })
def toCvImg(image: Image):
    return np.asarray(image)
def center_crop(img, dim):
    crop_img =img[dim[0][1]:dim[1][1], dim[0][0]:dim[1][0]]
    return crop_img
def getContoursArea(contours):
    cnt_area = np.array([])
    for cnt in contours:
        c_area = cv.contourArea(cnt)
        cnt_area = sorted(np.append(cnt_area, c_area ), reverse=True)
        return np.mean(cnt_area)
def predict_segment(image):
    image = toCvImg(image)
    # MASK SEGMENTATION
    blank = np.zeros(image.shape, dtype=np.uint8)
    # Detect results
    r = model.detect([image])[0]
    object_count = len(r["class_ids"])
    contour_count = 0
    result ={}
    for i in range(object_count):
        # 1. Mask
        mask = r["masks"][:, :, i]
        contours = get_mask_contours(mask)
        contoursArea = getContoursArea(contours)
        for cnt in contours:
            c_area = cv.contourArea(cnt)
            if(c_area >= contoursArea/2 and (c_area>=1000)):
                contour_count +=1
                min = np.amin(cnt, axis=0)
                max = np.amax(cnt, axis=0)
                dim_object = [min, max]
                # draw contour
                mask = cv.drawContours(blank.copy(), [cnt],0, (255,255,255), -1)
                new_img =cv.bitwise_and(image, mask)
                crop_img = center_crop(new_img, dim_object)
                cv_img = cv.cvtColor(cv.resize(crop_img, (150, 150)), cv.COLOR_BGR2RGB)
                # SAVE TO DRIVE
                # Preprocess 
                seg_img = preprocess(crop_img)
                # Extract features
                features = extract_features(seg_img)
                # Classify
                pred_result = predict(features)
                # SAVE TO DRIVE
                img_name = random.randint(0,9)
                img_path = f'prediction\Img_process\\resource\seg_img\img_{img_name}.jpg'
                cv.imwrite(img_path, cv_img)
                savedImg = saveToDrive(img_path, img_name)
                os.remove(img_path)
                # SAVE TO MONGODB
                savePredictResult(savedImg['image_url'], pred_result, savedImg['image_id'])
                # 
                response = {
                    "url" : savedImg['image_url'],
                    "status" : pred_result
                }
                result[f"l{contour_count}"] = response

    if(not contour_count): return 'Not found any leaf in the image case1'
    else: 
        return result
        
   


