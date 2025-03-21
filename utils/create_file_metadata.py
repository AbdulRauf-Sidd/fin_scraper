def create_file_metadata(file_name, file_type, date, path_to_file_on_r2, r2_url, content_type):
    # Get the current date in 'YYYY-MM-DD' format

    # Create and return the dictionary
    file_metadata = {
        "file_name": file_name,
        "file_type": file_type,
        "published_date": date,
        "r2_path": path_to_file_on_r2,
        "url": r2_url,
        "content_type": content_type  # Content type is expected to be a list of strings
    }
    
    return file_metadata