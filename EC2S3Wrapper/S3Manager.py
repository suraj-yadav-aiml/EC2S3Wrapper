import os
from typing import List, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class S3Manager:
    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
    ) -> None:
        """
        Initializes the S3Manager with an S3 client.

        Args:
            aws_access_key_id (Optional[str]): AWS access key ID. Defaults to None.
            aws_secret_access_key (Optional[str]): AWS secret access key. Defaults to None.
            region_name (Optional[str]): AWS region. Defaults to None.
        """
        if aws_access_key_id and aws_secret_access_key:
            # Use explicitly provided credentials
            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name,
            )
            print("S3 client initialized with provided credentials.")
        else:
            # Use default credentials from environment or IAM role
            self.s3 = boto3.client("s3")
            print("S3 client initialized using default credentials.")

    def list_buckets(self) -> Optional[List[str]]:
        """
        Retrieves and lists all S3 buckets associated with the AWS account.

        Returns:
            Optional[List[str]]: A list of bucket names if successful. Raises an exception if an error occurs.
        
        Raises:
            ClientError: If there is an issue with the S3 client request.
            NoCredentialsError: If AWS credentials are not found or improperly configured.
        """
        try:
            print("Fetching the list of buckets...")
            response = self.s3.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            # print(f"Buckets found: {buckets}")
            return buckets
        except ClientError as e:
            print(f"Error listing buckets: {e}")
            raise
        except NoCredentialsError:
            print("AWS credentials not found. Ensure they are set correctly.")
            raise
    
    def create_bucket(self, bucket_name: str) -> None:
        """
        Creates an S3 bucket if it does not already exist.

        Args:
            bucket_name (str): The name of the S3 bucket to create.

        Raises:
            ClientError: If there is an issue with the S3 client request.
            NoCredentialsError: If AWS credentials are not found or improperly configured.
        """
        try:
            # Check if the bucket already exists
            all_buckets = self.list_buckets()
            if bucket_name not in all_buckets:
                self.s3.create_bucket(Bucket=bucket_name)
                print(f"S3 Bucket with name '{bucket_name}' has been created successfully.")
            else:
                print(f"S3 Bucket '{bucket_name}' already exists.")
        except ClientError as e:
            print(f"Error creating bucket: {e}")
            raise
        except NoCredentialsError:
            print("AWS credentials not found. Ensure they are set correctly.")
            raise
    
    def upload_file(
            self,
            file_path: str,
            bucket_name: str,
            object_name: Optional[str] = None
        ) -> None:
        """
        Uploads a file to the specified S3 bucket.

        Args:
            file_path (str): The path to the file to upload.
            bucket_name (str): The name of the S3 bucket.
            object_name (Optional[str]): The object name in the S3 bucket (defaults to the file name).

        Raises:
            ClientError: If there is an issue with the file upload request.
            NoCredentialsError: If AWS credentials are not found or improperly configured.
        """
        if object_name is None:
            object_name = os.path.basename(file_path)

        try:
            self.s3.upload_file(Filename=file_path, Bucket=bucket_name, Key=object_name)
            print(f"File '{file_path}' uploaded to S3 as '{object_name}'")
        except ClientError as e:
            print(f"Error uploading file: {e}")
            raise
        except NoCredentialsError:
            print("AWS credentials not found. Ensure they are set correctly.")
            raise
    
    def list_objects_in_bucket(self, bucket_name: str) -> Optional[List[str]]:
        """
        Lists the object keys in the specified S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket to list the objects from.

        Returns:
            Optional[List[str]]: A list of object keys in the bucket if successful,
            or raises an exception if an error occurs.

        Raises:
            ClientError: If there is an issue with the S3 request, such as permission errors or invalid bucket names.
            NoCredentialsError: If AWS credentials are not found or are improperly configured.
        """
        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name)
            object_keys = [obj['Key'] for obj in response.get('Contents', [])]
            return object_keys
        except ClientError as e:
            print(f"Error listing objects in bucket '{bucket_name}': {e}")
            raise
        except NoCredentialsError:
            print("AWS credentials not found. Ensure they are set correctly.")
            raise
    
    def download_file(self, object_name: str, bucket_name: str, file_path: str) -> None:
        """
        Downloads a file from the specified S3 bucket to a local path.

        Args:
            object_name (str): The name of the object in the S3 bucket.
            bucket_name (str): The name of the S3 bucket.
            file_path (str): The local path where the file should be saved.

        Raises:
            ClientError: If there is an error in the S3 request, such as the object not being found or permission issues.
            NoCredentialsError: If AWS credentials are not found.
        """
        # Ensure the directory exists
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            print(f"{os.path.dirname(file_path)} directory created.")

        try:
            self.s3.download_file(Bucket=bucket_name, Key=object_name, Filename=file_path)
            print(f"Downloaded '{object_name}' from S3 bucket '{bucket_name}' to '{file_path}'")
        except ClientError as e:
            if e.response['Error']['Message'] == 'Not Found':
                print(f"Object '{object_name}' not found in bucket '{bucket_name}'")
            else:
                print(f"Error downloading file: {e}")
            raise 
        except NoCredentialsError:
            print("AWS credentials not found. Ensure they are set correctly.")
            raise 

    
    def upload_folder(
            self,
            directory_path: str,
            bucket_name: str,
            s3_prefix: Optional[str] = ""
    ) -> None:
        """
        Uploads the contents of a local folder to a specified S3 bucket.

        Args:
            directory_path (str): The path of the local directory to upload.
            bucket_name (str): The name of the S3 bucket where files will be uploaded.
            s3_prefix (Optional[str]): The prefix (folder path) in the S3 bucket. Defaults to the root of the bucket.

        Raises:
            FileNotFoundError: If the specified directory_path does not exist or is not accessible.
            ClientError: If an error occurs while uploading files to S3.
            NoCredentialsError: If AWS credentials are not found.
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"The directory '{directory_path}' does not exist or is inaccessible.")

        try:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    # Construct the full local path
                    file_path = os.path.join(root, file).replace("\\", "/")
                    
                    # Construct the S3 key with the specified prefix
                    relative_path = os.path.relpath(file_path, directory_path).replace("\\", "/")
                    s3_key = f"{s3_prefix}/{relative_path}".strip("/")  # Ensure no leading/trailing slashes

                    # Upload the file
                    self.s3.upload_file(Filename=file_path, Bucket=bucket_name, Key=s3_key)
                    print(f"Uploaded '{file_path}' to S3 bucket '{bucket_name}' as '{s3_key}'")
        except ClientError as e:
            print(f"Error uploading folder '{directory_path}' to bucket '{bucket_name}': {e}")
            raise
        except NoCredentialsError:
            print("AWS credentials not found. Ensure they are set correctly.")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise

    def download_s3_folder(self, bucket_name: str, s3_prefix: str, local_path: str) -> None:
        """
        Downloads a folder and its contents from an S3 bucket to a local directory.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_prefix (str): The prefix (folder path) in the S3 bucket to download.
            local_path (str): The local directory where the files will be saved.

        Raises:
            FileNotFoundError: If the specified local_path is inaccessible or cannot be created.
            ClientError: If an error occurs during the download process from S3.
            NoCredentialsError: If AWS credentials are not found.
        """
        # Ensure the local directory exists
        try:
            os.makedirs(local_path, exist_ok=True)
            print(f"Local directory '{local_path}' is ready for downloads.")
        except OSError as e:
            raise FileNotFoundError(f"Error creating or accessing local directory '{local_path}': {e}")

        # Paginator for handling large S3 folders
        paginator = self.s3.get_paginator("list_objects_v2")

        try:
            for page in paginator.paginate(Bucket=bucket_name, Prefix=s3_prefix):
                if "Contents" in page:
                    for obj in page["Contents"]:
                        s3_key = obj["Key"]
                        
                        # Preserve S3 folder structure locally
                        relative_path = os.path.relpath(s3_key, s3_prefix)
                        local_file_path = os.path.join(local_path, relative_path).replace("\\", "/")

                        # Ensure local directories for the file
                        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                        # Download the file
                        self.s3.download_file(Bucket=bucket_name, Key=s3_key, Filename=local_file_path)
                        print(f"Downloaded '{s3_key}' from bucket '{bucket_name}' to '{local_file_path}'")
                else:
                    print(f"No objects found in bucket '{bucket_name}' with prefix '{s3_prefix}'")
        except ClientError as e:
            print(f"Error downloading folder from S3 bucket '{bucket_name}' with prefix '{s3_prefix}': {e}")
            raise
        except NoCredentialsError:
            print("AWS credentials not found. Ensure they are set correctly.")
            raise
        except Exception as e:
            print(f"An unexpected error occurred during download: {e}")
            raise
    
    def delete_objects(self, bucket_name: str) -> None:
        """
        Deletes all objects in the specified S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.

        Raises:
            ClientError: If an error occurs while interacting with S3.
            NoCredentialsError: If AWS credentials are not found.
            Exception: For any unexpected errors during execution.
        """
        paginator = self.s3.get_paginator("list_objects_v2")
        
        try:
            # Iterate through pages of objects in the bucket
            for page in paginator.paginate(Bucket=bucket_name):
                if "Contents" in page:
                    # Prepare objects to delete
                    objects_to_delete = [{"Key": obj["Key"]} for obj in page["Contents"]]
                    
                    # Perform the delete operation
                    response = self.s3.delete_objects(Bucket=bucket_name, Delete={"Objects": objects_to_delete})

                    # Check for errors in the response
                    if "Errors" in response:
                        for error in response["Errors"]:
                            print(f"Error deleting object {error['Key']}: {error['Message']}")
                    else:
                        print(f"Successfully deleted {len(objects_to_delete)} objects from bucket '{bucket_name}'")
                else:
                    print(f"No objects found in bucket '{bucket_name}' to delete.")
        except ClientError as e:
            print(f"Error deleting objects from bucket '{bucket_name}': {e}")
            raise
        except NoCredentialsError:
            print("AWS credentials not found. Ensure they are set correctly.")
            raise
        except Exception as e:
            print(f"An unexpected error occurred while deleting objects from bucket '{bucket_name}': {e}")
            raise
    
    def delete_bucket(self, bucket_name: str) -> None:
        """
        Deletes the specified S3 bucket after ensuring it is empty.

        Args:
            bucket_name (str): The name of the S3 bucket to delete.

        Raises:
            ClientError: If an error occurs while interacting with S3.
            NoCredentialsError: If AWS credentials are not found.
            Exception: For any unexpected errors during execution.
        """
        try:
            # Check if the bucket exists
            all_buckets = self.list_buckets()
            if bucket_name not in all_buckets:
                print(f"Bucket '{bucket_name}' not found on S3.")
                return

            # Check if the bucket contains objects
            paginator = self.s3.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=bucket_name):
                if "Contents" in page:
                    print(f"Bucket '{bucket_name}' is not empty. \nDeleting all objects in {bucket_name}")
                    self.delete_objects(bucket_name)
                    break

            # Delete the bucket
            self.s3.delete_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' deleted successfully.")
        
        except ClientError as e:
            print(f"Error deleting bucket '{bucket_name}': {e}")
            raise
        except NoCredentialsError:
            print("AWS credentials not found. Ensure they are set correctly.")
            raise
        except Exception as e:
            print(f"An unexpected error occurred while deleting bucket '{bucket_name}': {e}")
            raise
