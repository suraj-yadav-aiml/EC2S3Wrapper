# EC2S3Wrapper

This repository provides a Python-based toolkit for managing AWS resources efficiently. The toolkit consists of two main modules: **EC2Manager** for managing Amazon EC2 instances and **S3Manager** for managing Amazon S3 buckets and objects. These modules are designed with production-grade best practices, including robust error handling, modular design, and scalability.

---

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Modules](#modules)
    - [EC2Manager](#ec2manager)
    - [S3Manager](#s3manager)
4. [Usage](#usage)
5. [License](#license)

---

## Features

- **EC2Manager**:
  - Manage EC2 instances: start, stop, terminate, retrieve public IPs.
  - Create and manage key EC2 instances.
  - Monitor EC2 instance states with a timeout feature.

- **S3Manager**:
  - Manage S3 buckets: create, list, delete buckets.
  - Upload and download files or entire folders to/from S3.
  - List and delete objects in a bucket.
  - Empty buckets before deletion.

---

## Installation

### Prerequisites
- Python 3.10 or above.
- AWS credentials configured using the AWS CLI or IAM access keys.

### Install Required Libraries
Install the dependencies using pip:

```bash
pip install boto3 
```

To install **EC2S3Wrapper**, you can use pip:

```bash
pip install EC2S3Wrapper

---

## Modules

### EC2Manager

**Overview**: The `EC2Manager` module simplifies managing EC2 instances. It supports key EC2 operations and integrates robust exception handling.

#### Key Functions:
1. **`list_instances`**: Lists all EC2 instances
2. **`start_instance`**: Starts an EC2 instance by instance ID.
3. **`stop_instance`**: Stops an EC2 instance by instance ID.
4. **`terminate_instance`**: Terminates an EC2 instance by instance ID.
5. **`create_key_pair`**: Creates an EC2 key pair and saves it as a `.pem` file.
6. **`get_instance_public_ip`**: Fetches the public IP address of an instance.

### S3Manager

**Overview**: The `S3Manager` module provides tools for managing S3 buckets and their contents. It ensures safe operations with extensive error handling.

#### Key Functions:
1. **`list_buckets`**: Lists all S3 buckets in the account.
2. **`create_bucket`**: Creates a new S3 bucket.
3. **`upload_file`**: Uploads a file to an S3 bucket.
4. **`upload_folder`**: Recursively uploads a folder and its contents to an S3 bucket.
5. **`download_file`**: Downloads a file from an S3 bucket.
6. **`download_s3_folder`**: Recursively downloads an entire folder from an S3 bucket to a local directory.
7. **`list_objects_in_bucket`**: Lists all objects in an S3 bucket.
8. **`delete_objects`**: Deletes all objects in a bucket.
9. **`delete_bucket`**: Deletes a bucket after ensuring it is empty.

---

## Usage

### Setting Up AWS Credentials
AWS credentials can be passed directly or set up in the default AWS CLI profile.

### Example Usage

#### Initialize EC2Manager and S3Manager
```python
from ec2_manager import EC2Manager
from s3_manager import S3Manager

# Initialize EC2Manager
ec2_manager = EC2Manager(
    aws_access_key_id="your_access_key",
    aws_secret_access_key="your_secret_key",
    region_name="us-east-1"
)

# Initialize S3Manager
s3_manager = S3Manager(
    aws_access_key_id="your_access_key",
    aws_secret_access_key="your_secret_key",
    region_name="us-east-1"
)
```

#### Working with EC2 Instances
```python
# List all EC2 instances
instances = ec2_manager.list_instances()
print(instances)

# Start an EC2 instance
ec2_manager.start_instance(instance_id="i-0123456789abcdef0")

# Fetch public IP of an instance
public_ip = ec2_manager.get_instance_public_ip(instance_id="i-0123456789abcdef0")
print(f"Public IP: {public_ip}")
```

#### Managing S3 Buckets and Objects
```python
# List all S3 buckets
buckets = s3_manager.list_buckets()
print(buckets)

# Create a new bucket
s3_manager.create_bucket(bucket_name="my-new-bucket")

# Upload a file
s3_manager.upload_file(file_path="path/to/local/file.txt", bucket_name="my-new-bucket")

# Download a file
s3_manager.download_file(
    object_name="file.txt",
    bucket_name="my-new-bucket",
    file_path="path/to/local/file.txt"
)

# Delete a bucket
s3_manager.delete_bucket(bucket_name="my-new-bucket")
```

--- 

This toolkit is designed to simplify AWS resource management while ensuring robust and production-grade functionality. Contributions and suggestions are welcome! 😊