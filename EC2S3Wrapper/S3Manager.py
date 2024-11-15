import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Optional

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



