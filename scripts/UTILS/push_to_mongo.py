from pymongo import MongoClient

# Connect to the MongoDB server
client = MongoClient('mongodb://localhost:27017/')

# Select the database
db = client['mydatabase']

# Select the collection
collection = db['mycollection']

# Insert a document
collection.insert_one(my_json_document)