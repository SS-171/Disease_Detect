import requests
import os
predict_url = 'http://192.168.137.1:8000/disease/predict'
diseases = ['Early_blight', "Late_blight", "Bacterial_spot", "Yellow_Leaf_Curl_Virus"]

def json_extract(data):
    count = 0
    if not (isinstance(data, str)):
        for item in data.values():
            disease = item['status']
            if disease in diseases:
                count = count + 1
            
    if count: 
      print(f'Detect {count} disease')
    else :
      print('None of disease detected')
    return count

def imgPredict(path):
    disease_count = 0
    with open(path, 'rb') as img:
        name_img= os.path.basename(path)
        files= {'file': (name_img,img,'multipart/form-data',{'Expires': '0'}) }
        with requests.Session() as s:
            global response
            r = s.post(predict_url,files=files)
            response = r
            disease_count = json_extract(r.json())
            print("predict status",r.status_code)
    # os.remove(path)
    return {"count": disease_count, "response":response.json()}

print(imgPredict("prediction\static\img\\bacterialSpot\\1.JPG"))