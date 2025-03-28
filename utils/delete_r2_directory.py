import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def empty_r2_directory(bucket_name, directory_prefix):
    # Initialize the S3 client with Cloudflare R2 credentials
    s3 = boto3.client(
        's3',
        endpoint_url="https://3c5636b6cfe0011ec1887ff62b057097.r2.cloudflarestorage.com",
        aws_access_key_id="f1ac1dc043a240f996be558cfba72868",
        aws_secret_access_key="de1dd032fe83dc7bc8b8f8b207ca54807fa851b07483428396c141ebaf46d8bb"
    )

    try:
        # List all objects in the bucket with the specified prefix (directory)
        paginator = s3.get_paginator('list_objects_v2')
        
        for page in paginator.paginate(Bucket=bucket_name, Prefix=directory_prefix):
            if 'Contents' in page:
                # Get list of objects to delete
                objects_to_delete = [{'Key': obj['Key']} for obj in page['Contents']]
                
                # Delete objects in batch if any exist
                if objects_to_delete:
                    s3.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': objects_to_delete}
                    )
                    print(f"Deleted {len(objects_to_delete)} objects from directory '{directory_prefix}'")

        print(f"Successfully emptied the directory '{directory_prefix}' in the R2 bucket")

    except Exception as e:
        print(f"Error emptying directory in bucket: {str(e)}")

if __name__ == "__main__":
    # Define the bucket name and directory prefix
    bucket_name = "fin-scraping-bucket"
    directory_prefix = "OR/"  # Make sure this ends with a slash to specify it as a directory
    empty_r2_directory(bucket_name, directory_prefix)
