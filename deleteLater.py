import os
import json
from pymongo import MongoClient

# MongoDB Connection String
connection_string = "mongodb+srv://scraperDB:MDa19wILenT3qXDb@cluster0.m9ie4.mongodb.net/"

# Create MongoDB Client
client = MongoClient(connection_string)

# Specify Database and Collection
db = client['json_storage']
collection = db['json_files']

# Directory Containing JSON Files
base_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
relative_directory = 'fin_scraper/JSONS'
directory_path = os.path.join(base_directory, relative_directory)
print(f"JSON files directory: {directory_path}")

# 1) Drop the current collection to ensure a full overwrite
collection.drop()

# 2) Insert the JSON files from scratch
for filename in os.listdir(directory_path):
    if filename.endswith(".json"):  # Only process JSON files
        file_path = os.path.join(directory_path, filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)

            # If the JSON is a dictionary, insert as a single document
            if isinstance(json_data, dict):
                collection.insert_one(json_data)
                print(f"Inserted 1 document from: {filename}")

            # If the JSON is a list, insert them all
            elif isinstance(json_data, list):
                if len(json_data) > 0:
                    collection.insert_many(json_data)
                    print(f"Inserted {len(json_data)} documents from: {filename}")
                else:
                    print(f"Skipping {filename}: JSON array is empty.")

            else:
                print(f"Skipping {filename}: JSON format not supported.")

        except Exception as e:
            print(f"Failed to process {filename}: {e}")
