from pymongo import MongoClient

client = MongoClient("mongodb+srv://client_user:WUdvCac5js1N0SMl@cluster0.m9ie4.mongodb.net/")
db = client["json_storage"]
collection = db["json_files"]

# Fetch a sample document
sample_data = collection.find_one()
print(sample_data)

