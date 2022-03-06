from PIL import Image
from io import BytesIO
import tensorflow as tf
import cv2 as cv
import tensorflow_hub as hub
import numpy as np
import xgboost as xgb 
import keras
input_shape = (150, 150)
base_model = keras.models.load_model("prediction/Img_process/resource/base_model.h5")
xgmodel = xgb.Booster()
xgmodel.load_model('prediction//Img_process//resource//xgb_model2.bin')
labels = ['Bacterial_spot', 'Early_blight', 'Late_blight',
           'Yellow_Leaf_Curl_Virus', 'healthy']

def read_image(file) ->Image.Image:
    pil_image = Image.open(BytesIO(file))
    return pil_image

def preprocess(image):
    # IF NOT SEG 
    # image = cv.resize(np.asfarray(image), input_shape)
    
    # IF SEG
    image =  np.float32(image)
    image = cv.resize(image, input_shape)
    # 
    image = image/255
    image = np.expand_dims(image, 0)
    return image
    
# def preprocess1(image):
#     # IF NOT SEG 
#     image = cv.resize(np.asfarray(image), input_shape)
    
#     # 
#     image = image/255
#     image = np.expand_dims(image, 0)
#     return image
def extract_features(img):
    feature = base_model.predict(img)
    features = feature.reshape(feature.shape[0], -1)
    d_image = xgb.DMatrix(features)
    return d_image
def predict(d_image):
    index = np.argmax(xgmodel.predict(d_image)[0])
    result_label = labels[index]
    return result_label