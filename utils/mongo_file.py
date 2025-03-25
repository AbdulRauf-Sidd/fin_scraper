import os
import json
import argparse
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
relative_directory = 'JSONS/'
directory_path = os.path.join(base_directory, relative_directory)

# Function to Check if Document Needs an Update
def needs_update(existing_doc, new_data):
    """Compare the existing document and new data to check for differences."""
    if not existing_doc:
        return True  # No document exists, so we need to insert
    del existing_doc["_id"]  # Remove MongoDB's internal ID before comparison
    return existing_doc != new_data  # Return True if there is a difference

# Parse Command-Line Arguments
parser = argparse.ArgumentParser(description="Push a specific JSON file to MongoDB")
parser.add_argument("filename", help="Name of the JSON file to push")
args = parser.parse_args()
specific_file = args.filename

# Construct full file path
file_path = os.path.join(directory_path, specific_file)

# Check if the specified file exists
if os.path.exists(file_path):
    try:
        # Open and Read the JSON File
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        # If the JSON is a Dictionary, Handle Single Document
        if isinstance(json_data, dict):
            unique_key = {"file_name": json_data.get("file_name", specific_file)}
            existing_doc = collection.find_one(unique_key)

            if needs_update(existing_doc, json_data):
                collection.update_one(unique_key, {"$set": json_data}, upsert=True)
                print(f"Updated or Inserted: {specific_file}")
            else:
                print(f"No changes detected: {specific_file}")

        # If the JSON is a List, Handle Multiple Documents
        elif isinstance(json_data, list):
            updated_count = 0
            inserted_count = 0

            for doc in json_data:
                unique_key = {"file_name": doc.get("file_name", specific_file)}
                existing_doc = collection.find_one(unique_key)

                if needs_update(existing_doc, doc):
                    collection.update_one(unique_key, {"$set": doc}, upsert=True)
                    updated_count += 1
                else:
                    inserted_count += 1

            print(f"Processed {specific_file}: {updated_count} updated, {inserted_count} unchanged.")

        else:
            print(f"Skipping {specific_file}: JSON format not supported")

    except Exception as e:
        print(f"Failed to process {specific_file}: {e}")

else:
    print(f"File not found: {specific_file}")
