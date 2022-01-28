from pymongo import MongoClient
conn = MongoClient("mongodb://localhost:27017")
plantDb = conn["plant"]
PlantCollection = plantDb["predict"]
EnviCollection = plantDb['Environment']
UserCollection = plantDb['User']
LogCollection = plantDb['Log']
