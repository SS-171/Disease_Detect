from pymongo import MongoClient

cluster = MongoClient()
db = cluster["plant"]
collection = db["test"]
post1 = {"_id":5, "name": "joe"}
post2 = {"_id": 6, "name":"Bill"}
results = collection.insert_many(post1, post2)
results = collection.find_one({"_id": 2})
results = collection.find({"_id":"", "name":""})
# find everything
results = collection.find({})
results = collection.delete_one({"id":1})
results = collection.delete_many({})
# insert
resuts = collection.insert_many([post1, post2])
results = collection.update_one({"_id": 5}, {"$set" :{"hello": 5}})
# some operators can consider like $max, $null... in mongoDb
# count document the meet the citeria

post_count = collection.count_documents({})
print(post_count)