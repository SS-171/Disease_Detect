# python -m venv myEnv
# myEnv
import cv2 as cv
import numpy as np
import os 
from datetime import datetime
from PIL import Image
import random
import matplotlib.pyplot as plt
MODEL_DIR = "prediction/Img_process/resource/model5.h5"
from prediction.Img_process.source import get_mask_contours, load_inference_model
from prediction.Img_process.classify import  preprocess,extract_features, predict
num_classes = 1
model, inference_config = load_inference_model(num_classes, MODEL_DIR)
def getPredictTime():
    now = datetime.now()
    nowStr = now.strftime("%Y-%m-%d %H:%M:%S")
    return nowStr

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


def predict_segment(url):
    # image  = preprocess(image)
    result = {}
    img = cv.imread(url)
    image = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    
    
    # MASK SEGMENTATION
    blank = np.zeros(image.shape, dtype=np.uint8)
    # Detect results
    r = model.detect([image])[0]
    object_count = len(r["class_ids"])
    contour_count = 0
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
                img_mask = cv.drawContours(blank.copy(), [cnt],0, (255,255,255), -1)
                new_img =cv.bitwise_and(image, img_mask)
                crop_img = cv.resize(center_crop(new_img, dim_object),(150,150))
                cv_img = cv.cvtColor(crop_img, cv.COLOR_BGR2RGB)
                # seg_img = preprocess(crop_img)
                # features = extract_features(seg_img)
                # pred_result = predict(features)
                img_name = random.randint(0,400)
                img_path = f'prediction\Img_process\\resource\seg_img\img_{img_name}.jpg'
                # cv.imshow("image", cv_img)
                # cv.waitKey(0)
                cv.imwrite(img_path, cv_img)
                # os.remove(img_path)
               
    #             response = {
                
    #                 "status" : pred_result
    #             }
    #             result[f"l{contour_count}"] = response

    # if(not contour_count): return 'Not found any leaf in the image case1'
    # else: 
    #     return result
        
   
for i in range(43,56):
    predict_segment(f"prediction\static\img\\real_img\\ras_img\\{i}.jpg")
