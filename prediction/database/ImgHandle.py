# from pymongo import MongoClient
# from PIL import Image
# import io
# import gridfs
# from .config.db import conn
# import numpy as np
# from numpy import asarray
# from PIL import Image
# import blosc
# db = conn['plant']
# fs = gridfs.GridFS(db)
# def saveIm(img_arr):
#     compressed_bytes = blosc
from PIL import Image
from .config.db import conn
import matplotlib
import matplotlib.pyplot as plt
import io
import cv2 as cv
from bson import ObjectId
plantDb = conn["plant"]
collection = plantDb["predict"]

def toPIL(imgArr):
    im = Image.fromarray(imgArr.astype('uint8'), 'RGB')
    image_bytes = io.BytesIO()
    im.save(image_bytes, format="JPEG")
    # image = {
    #     "segImage": image_bytes.getvalue()
    # }
    return image_bytes.getvalue()
    # collection.insert_one(image)
# def readImg(id):
#     image =collection.find_one({"_id": ObjectId(id)})
#     pil_img = Image.open(io.BytesIO(image['segImage']))
#     plt.imshow(pil_img)
#     plt.show()
