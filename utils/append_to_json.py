import os
import json

def append_to_json_file(file_path, new_data):
    # Check if file exists and has content
    if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
        # File exists and has content, read the current data
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                if isinstance(data, list):  # Only append if the existing data is a list
                    data.extend(new_data)
                else:
                    data = [data] + new_data  # Make it a list and append new data
            except json.JSONDecodeError:
                data = new_data  # If JSON is invalid, start new
    else:
        # File does not exist or is empty, start new list
        data = new_data

    # Write the updated data back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2)