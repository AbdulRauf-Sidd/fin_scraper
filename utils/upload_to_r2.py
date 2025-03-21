import os
import boto3
from pathlib import Path

# Set up your Cloudflare R2 credentials and endpoint
access_key = os.getenv('R2_ACCESS_KEY')
secret_key = os.getenv('R2_SECRET_KEY')
endpoint_url = os.getenv('R2_ENDPOINT_URL')

# Create a session using your credentials

r2_folder = 'why/bye/world/'  # Set your desired folder path within R2


# Function to upload a single file and return the R2 URL
def upload_file_to_r2(file_path, r2_folder):
    session = boto3.session.Session()
    s3 = session.client('s3', 
                   aws_access_key_id=access_key, 
                   aws_secret_access_key=secret_key, 
                   endpoint_url=endpoint_url)   
    # Check if the file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # Extract the filename from the file path
    filename = os.path.basename(file_path)

    # Construct the R2 key by combining the folder and the filename
    r2_file_key = os.path.join(r2_folder, filename)

    # Upload the file to R2
    with open(file_path, 'rb') as data:
        s3.put_object(Bucket='fin-scraping-bucket', Key=r2_file_key, Body=data)

    # Construct the URL of the uploaded file
    file_url = f'{endpoint_url}/fin-scraping-bucket/{r2_file_key}'
    print(f"Uploaded: {r2_file_key}, URL: {file_url}")
    
    return file_url

upload_file_to_r2('why/bye/world/qwerty.txt', r2_folder)
