import os
import boto3
from pathlib import Path
import time
from urllib.parse import quote
# from dotenv import load_dotenv

# base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# env_path = os.path.join(base_path, '.env')
# load_dotenv(env_path)

# Load the .env file
# Set up your Cloudflare R2 credentials and endpoint
access_key = 'f1ac1dc043a240f996be558cfba72868'
secret_key = 'de1dd032fe83dc7bc8b8f8b207ca54807fa851b07483428396c141ebaf46d8bb'
endpoint_url = 'https://3c5636b6cfe0011ec1887ff62b057097.r2.cloudflarestorage.com'

# Create a session using your credentials

# r2_folder = 'why/bye/world/'  # Set your desired folder path within R2


# Function to upload a single file and return the R2 URL
def upload_file_to_r2(file_path, r2_folder, test_run):
    session = boto3.session.Session()
    if test_run == 'true':
        s3 = session.client('s3', 
                       aws_access_key_id='f1ac1dc043a240f996be558cfba72868', 
                       aws_secret_access_key="de1dd032fe83dc7bc8b8f8b207ca54807fa851b07483428396c141ebaf46d8bb", 
                       endpoint_url="https://3c5636b6cfe0011ec1887ff62b057097.r2.cloudflarestorage.com") 
        bucket_name = 'fin-scraping-bucket'
        public_url = 'https://pub-43b7342d87a7428998f14a200ddd2a26.r2.dev/'
    else:
        s3 = session.client('s3', 
                       aws_access_key_id='75ab8895b1384c0274072b23d0eb9d3d', 
                       aws_secret_access_key="eb384a4f3bc3c5504ec6c5ee355d4b1358ab191a6968f0521f83e330992882ef", 
                       endpoint_url="https://3f80db7adc544850c6ad4904a0fb8f54.r2.cloudflarestorage.com") 
        bucket_name = 'equity-data'
        public_url = 'https://pub-2c783279b61043e19fbdadd1bee5153a.r2.dev/'
 
    # Check if the file exists
    # if not os.path.isfile(file_path):
    #     continue
        # raise FileNotFoundError(f"The file {file_path} does not exist.")

    # Extract the filename from the file path
    filename = os.path.basename(file_path)

    # Construct the R2 key by combining the folder and the filename
    r2_file_key = os.path.join(r2_folder, filename)

    # Upload the file to R2
    attempts = 0
    while attempts < 3:
        try:
            # Upload the file to R2
            with open(file_path, 'rb') as data:
                s3.put_object(Bucket=bucket_name, Key=r2_file_key, Body=data)

            # Construct the URL of the uploaded file
            safe_r2_file_key = quote(r2_file_key)
            file_url = f'{public_url}{safe_r2_file_key}'
            print(f"Uploaded: {r2_file_key}, URL: {file_url}")
            return file_url

        except Exception as e:
            attempts += 1
            print(f"Attempt {attempts}: Failed to upload file. Error: {str(e)}")
            if attempts < 3:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("Maximum retry attempts reached, failed to upload.")
                return None

# upload_file_to_r2('downloads/_cs_ferrari_05.05.2021_eng_0.pdf', "test/")
