import os
import glob
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Update the URI with your credentials and cluster details.
uri = "mongodb+srv://scraperDB:MDa19wILenT3qXDb@cluster0.m9ie4.mongodb.net/"

# Connect to the MongoDB Atlas cluster.
client = MongoClient(uri, server_api=ServerApi('1'))

# Ping the deployment to ensure the connection is successful.
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Failed to connect to MongoDB Atlas:", e)
    exit(1)

# Specify the database and collection names.
db = client["myDatabase"]         # Replace with your target database name.
collection = db["myCollection"]   # Replace with your target collection name.

# Define the directory containing the JSON files.
json_directory = "Completed/JSONS"  # Ensure this path is correct relative to your script.

# Use glob to get a list of all JSON files in the directory.
json_files = glob.glob(os.path.join(json_directory, "*.json"))

if not json_files:
    print("No JSON files found in the directory:", json_directory)
    exit(1)

# Loop over each file and insert the content into MongoDB.
for file_path in json_files:
    print(f"Processing file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
            # If data is a list (multiple documents) use insert_many,
            # otherwise use insert_one for a single document.
            if isinstance(data, list):
                result = collection.insert_many(data)
                print(f"Inserted {len(result.inserted_ids)} documents from {file_path}")
            else:
                result = collection.insert_one(data)
                print(f"Inserted document with id {result.inserted_id} from {file_path}")
    except json.JSONDecodeError as je:
        print(f"Error decoding JSON from file {file_path}: {je}")
    except Exception as ex:
        print(f"Error processing file {file_path}: {ex}")