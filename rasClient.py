import os
import requests
url = 'http://127.0.0.1:8000/disease/predict'
path_img = "prediction\static\img\\bacterialSpot\\1.JPG"
with open(path_img, 'rb') as img:
  name_img= os.path.basename(path_img)
  files= {'file': (name_img,img,'multipart/form-data',{'Expires': '0'}) }
  with requests.Session() as s:
    r = s.post(url,files=files)
    print(r.status_code)