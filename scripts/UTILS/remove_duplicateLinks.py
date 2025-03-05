import json

def remove_duplicates(input_file, output_file):
    # Load the JSON data from the input file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Set to track unique URLs
    seen_urls = set()
    unique_data = []

    # Iterate through the records
    for record in data:
        # Check for duplicates in the 'data' field (if it exists)
        if 'data' in record:
            # Create a list to store unique data entries for the current record
            unique_data_entries = []
            
            # Iterate through the 'data' field to remove duplicate source_urls
            for entry in record['data']:
                source_url = entry.get('source_url', None)
                
                # If source_url is not in seen_urls, add this entry to the unique_data_entries list
                if source_url and source_url not in seen_urls:
                    unique_data_entries.append(entry)
                    seen_urls.add(source_url)
            
            # Update the 'data' field in the record with the filtered unique data
            record['data'] = unique_data_entries

        # Append the record to the unique_data list
        unique_data.append(record)

    # Write the unique data back to the output file
    with open(output_file, 'w') as f:
        json.dump(unique_data, f, indent=4)

    print(f"Duplicates removed. Unique data written to {output_file}.")

# Specify the input and output files
input_json = 'merged_output.json'  # The original JSON file with potential duplicates
output_json = 'cleanedMerged_output.json'  # The file where unique data will be saved

# Call the function
remove_duplicates(input_json, output_json)