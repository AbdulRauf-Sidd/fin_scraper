from pymongo import MongoClient

# MongoDB Connection String
connection_string = "mongodb+srv://scraperDB:MDa19wILenT3qXDb@cluster0.m9ie4.mongodb.net/"

# Create MongoDB Client
client = MongoClient(connection_string)

# Specify Database and Collection
db = client['json_storage']
collection = db['json_files']

# Delete All Documents
result = collection.delete_many({})
print(f"Deleted {result.deleted_count} documents from the collection.")
