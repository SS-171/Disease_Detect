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
MODEL_DIR = "prediction/Img_process/resource/model1.h5"
from .source import get_mask_contours, load_inference_model
from .classify import  preprocess,extract_features, predict
num_classes = 1
model, inference_config = load_inference_model(num_classes, MODEL_DIR)
def getPredictTime():
    now = datetime.now()
    nowStr = now.strftime("%Y-%m-%d %H:%M:%S")
    return nowStr
def savePredictResult(url, status):
    now = getPredictTime().split(" ")
    PlantCollection.insert_one({
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
def predict_segment(image):
    # image  = preprocess(image)
    image = toCvImg(image)
    # MASK SEGMENTATION
    blank = np.zeros(image.shape, dtype=np.uint8)
    # Detect results
    r = model.detect([image])[0]
    object_count = len(r["class_ids"])
    # try:
    # srcID = ('%06x' % random.randrange(16**6)).upper()

    contour_count = 0
    cnt_area = np.array([])
    result ={}
    for i in range(object_count):
        # 1. Mask
        mask = r["masks"][:, :, i]
        contours = get_mask_contours(mask)
        for cnt in contours:
            c_area = cv.contourArea(cnt)
            cnt_area = sorted(np.append(cnt_area, c_area ), reverse=True)
            if(c_area >= np.mean(cnt_area)/2 and (c_area>=1000)):
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
                # img_number = random.randint(0, 200)
                # cv.imwrite(f'prediction\Img_process\\resource\seg_img\img_{img_number}.jpg', cv_img)
                # cv.waitKey(500)
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
                img_url = saveToDrive(img_path, img_name)
                os.remove(img_path)
                # SAVE TO MONGODB
                savePredictResult(img_url, pred_result)
                
                # 
                response = {
                    "url" : img_url,
                    "status" : pred_result
                }
                result[f"l{contour_count}"] = response

    if(not contour_count): return 'Not found any leaf in the image case1'
    else: 
        return result
        
    # except:
    #     return 'Not found any leaf in the image case2'



