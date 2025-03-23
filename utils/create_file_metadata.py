def create_file_metadata(file_name, file_type, date, r2_url, content_type):
    # Get the current date in 'YYYY-MM-DD' format

    # Create and return the dictionary
    file_metadata = {
        "file_name": file_name,
        "file_type": file_type,
        "published_date": date,
        "url": r2_url,
        "content_type": content_type  # Content type is expected to be a list of strings
    }
    
    return file_metadata