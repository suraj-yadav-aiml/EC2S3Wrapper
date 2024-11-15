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
            if e.response['Error']['Code'] == 'NoSuchKey':
                print(f"Object '{object_name}' not found in bucket '{bucket_name}'")
            else:
                print(f"Error downloading file: {e}")
            raise 
        except NoCredentialsError:
            print("AWS credentials not found. Ensure they are set correctly.")
            raise 

