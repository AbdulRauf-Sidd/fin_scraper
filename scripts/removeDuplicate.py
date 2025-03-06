import os
import json

def remove_duplicates(relative_directory):
    # Convert the relative directory to an absolute path
    directory = os.path.join(base_directory, relative_directory)

    # Verify if the directory exists
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return

    # List all files in the specified directory
    try:
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                input_file = os.path.join(directory, filename)
                print(f"Processing {input_file}...")

                with open(input_file, 'r') as f:
                    data = json.load(f)

                seen_urls = set()
                unique_data = []
                duplicate_count = 0

                for record in data:
                    if 'data' in record:
                        unique_data_entries = []
                        initial_count = len(record['data'])

                        for entry in record['data']:
                            source_url = entry.get('source_url', None)

                            if source_url and source_url not in seen_urls:
                                unique_data_entries.append(entry)
                                seen_urls.add(source_url)

                        # Update the record with unique entries
                        record['data'] = unique_data_entries
                        # Calculate number of duplicates removed
                        duplicate_count += (initial_count - len(unique_data_entries))

                    unique_data.append(record)

                # Overwrite the original file with the unique data
                with open(input_file, 'w') as f:
                    json.dump(unique_data, f, indent=4)

                # Log the number of duplicates removed
                print(f"Duplicates removed from {input_file}: {duplicate_count}")
    except PermissionError:
        print(f"Permission denied: Unable to access {directory}")

# Define the base directory relative to the script file
base_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# Specify the relative directory from the project root
relative_directory = 'JSONS'

# Call the function to process all JSON files in the directory
remove_duplicates(relative_directory)
