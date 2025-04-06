import boto3
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

def empty_r2_directory(bucket_name, directory_prefix):
    # Initialize the S3 client with Cloudflare R2 credentials
    s3 = boto3.client('s3', 
                       aws_access_key_id='75ab8895b1384c0274072b23d0eb9d3d', 
                       aws_secret_access_key="eb384a4f3bc3c5504ec6c5ee355d4b1358ab191a6968f0521f83e330992882ef", 
                       endpoint_url="https://3f80db7adc544850c6ad4904a0fb8f54.r2.cloudflarestorage.com") 

    try:
        # Get the current time and subtract 1 hour to compare the LastModified time
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        # List all objects in the bucket with the specified prefix (directory)
        paginator = s3.get_paginator('list_objects_v2')
        
        for page in paginator.paginate(Bucket=bucket_name, Prefix=directory_prefix):
            if 'Contents' in page:
                # Get list of objects to delete that were modified within the last hour
                objects_to_delete = []
                for obj in page['Contents']:
                    # Convert the LastModified time to UTC datetime
                    last_modified = obj['LastModified']
                    
                    # If the object was modified within the last hour, add to the list to delete
                    if last_modified >= one_hour_ago:
                        objects_to_delete.append({'Key': obj['Key']})

                # Delete objects in batch if any exist
                if objects_to_delete:
                    s3.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': objects_to_delete}
                    )
                    print(f"Deleted {len(objects_to_delete)} objects from directory '{directory_prefix}'")

        print(f"Successfully emptied the directory '{directory_prefix}' in the R2 bucket (only files from last hour)")

    except Exception as e:
        print(f"Error emptying directory in bucket: {str(e)}")

if __name__ == "__main__":
    # Define the bucket name and directory prefix
    bucket_name = 'equity-data'
    directory_prefix = "WISE/"  # Make sure this ends with a slash to specify it as a directory
    empty_r2_directory(bucket_name, directory_prefix)
