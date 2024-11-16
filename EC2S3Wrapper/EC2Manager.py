import os
import time
from typing import Optional, List

import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from tabulate import tabulate


class EC2Manager:
    """
    A class to manage EC2 instances and associated AWS resources using boto3.
    
    Attributes:
        ec2 (boto3.client): The EC2 client to interact with EC2 services.
        iam (boto3.client): The IAM client to interact with IAM services.
    """

    def __init__(
            self,
            aws_access_key_id: Optional[str] = None,
            aws_secret_access_key: Optional[str] = None,
            region_name: Optional[str] = None
    ) -> None:
        """
        Initializes the EC2Manager with boto3 EC2 and IAM clients. You can provide AWS credentials 
        and region programmatically.
        
        Args:
            aws_access_key_id (Optional[str]): The AWS Access Key ID. If not provided, uses the default credentials.
            aws_secret_access_key (Optional[str]): The AWS Secret Access Key. If not provided, uses the default credentials.
            region_name (Optional[str]): The AWS region to connect to. If not provided, uses the default region.

        If no credentials are provided, the method will attempt to use the default AWS credentials 
        (configured via `aws configure` or environment variables).
        """
        if aws_access_key_id and aws_secret_access_key:
            # If credentials are passed, use them directly
            self.ec2 = boto3.client('ec2', 
                                    aws_access_key_id=aws_access_key_id,
                                    aws_secret_access_key=aws_secret_access_key,
                                    region_name=region_name)
            self.iam = boto3.client('iam', 
                                    aws_access_key_id=aws_access_key_id,
                                    aws_secret_access_key=aws_secret_access_key,
                                    region_name=region_name)
        else:
            # Use default credentials if no keys are provided
            self.ec2 = boto3.client('ec2')
            self.iam = boto3.client('iam')
    
    def list_all_instances(self, get_count_message: bool = True) -> Optional[List[dict]]:
        """
        Fetches and displays details of all EC2 instances in the AWS account.

        This method retrieves information about all EC2 instances using the 
        `describe_instances` API call. It organizes the instance details into a list of dictionaries, 
        with each dictionary representing a single EC2 instance. 

        Additionally, if a "Name" tag is associated with an instance, it is included in the results.

        Args:
            get_count_message (bool): If True, displays a message with the count of instances 
                                    found. Defaults to True.

        Returns:
            Optional[List[dict]]: A list of dictionaries containing details of EC2 instances. 
                                Each dictionary contains the following keys:
                                - "InstanceID": The ID of the instance.
                                - "State": The current state of the instance (e.g., running, stopped, terminated, pending, ).
                                - "InstanceType": The type of instance (e.g., t2.micro).
                                - "PublicIP": The public IP address of the instance (or 'N/A' if not assigned).
                                - "PrivateIP": The private IP address of the instance (or 'N/A' if not assigned).
                                - "LaunchTime": The launch time of the instance in 'YYYY-MM-DD HH:MM:SS' format.
                                - "Name": The value of the "Name" tag, if present (or 'N/A' if not set).

        Raises:
            ClientError: If there is an error in communicating with the AWS API.
            NoCredentialsError: If AWS credentials are not set or found.
        """
        try:
            print("Fetching details of all EC2 instances...")
            response = self.ec2.describe_instances()

            # Instance extraction using list comprehension with Name tag handling
            instances = [
                {
                    "Name": next(
                        (tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'),
                        'N/A'
                    ),
                    "InstanceID": instance['InstanceId'],
                    "State": instance['State']['Name'],
                    "InstanceType": instance['InstanceType'],
                    "PublicIP": instance.get('PublicIpAddress', 'N/A'),
                    "PrivateIP": instance.get('PrivateIpAddress', 'N/A'),
                    "LaunchTime": instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S'),
                    
                }
                for reservation in response['Reservations']
                for instance in reservation['Instances']
            ]

            if instances:
                if get_count_message:
                    print(f"Found {len(instances)} instances.")
            else:
                print("No EC2 instances found.")
            return instances

        except ClientError as e:
            print(f"Error listing EC2 instances: {e}")
            raise
        except NoCredentialsError:
            print("AWS credentials not found. Ensure they are set correctly.")
            raise
    
    def list_all_instances_in_table(self) -> None:
        """
        Fetches and displays details of all EC2 instances in a nicely formatted table.

        Raises:
            Exception: If no instances are found or any other error occurs.
        """
        try:
            # Call list_all_instances() method
            instances = self.list_all_instances(get_count_message=False)

            # Check if there are any instances
            if not instances:
                print("No EC2 instances found.")
                return

            # Format data for display
            headers = ["Name", "InstanceID", "State", "InstanceType", "PublicIP", "PrivateIP", "LaunchTime"]
            table_data = []

            for instance in instances:
                table_data.append([
                    instance['Name'],
                    instance["InstanceID"],
                    instance["State"],
                    instance["InstanceType"],
                    instance["PublicIP"],
                    instance["PrivateIP"],
                    instance["LaunchTime"],
                ])

            # Display instances in a table format
            print(tabulate(table_data, headers=headers, tablefmt="grid"))

        except Exception as e:
            print(f"Error displaying EC2 instances: {e}")
            raise

    
    def get_instance_details_by_id(self, instance_id: str) -> Optional[dict]:
        """
        Retrieves detailed information about a specific EC2 instance.

        Args:
            instance_id (str): The ID of the EC2 instance.

        Returns:
            Optional[dict]: A dictionary containing detailed instance information or None if not found.
        """
        try:
            response = self.ec2.describe_instances(InstanceIds=[instance_id])
            if response['Reservations']:
                instance = response['Reservations'][0]['Instances'][0]
                return {
                    "Name": next(
                        (tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'),
                        'N/A'
                    ),
                    "InstanceID": instance['InstanceId'],
                    "State": instance['State']['Name'],
                    "InstanceType": instance['InstanceType'],
                    "PublicIP": instance.get('PublicIpAddress', 'N/A'),
                    "PrivateIP": instance.get('PrivateIpAddress', 'N/A'),
                    "LaunchTime": instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                print(f"No instance found with ID '{instance_id}'.")
                return None
        except ClientError as e:
            print(f"Error retrieving instance details: {e}")
            raise
    
    def get_instance_details_by_name(self, name: str) -> Optional[dict]:
        """
        Retrieves detailed information about an EC2 instance using its name tag.

        Args:
            name (str): The name of the EC2 instance (as specified in the Name tag).

        Returns:
            Optional[dict]: A dictionary containing the instance details, or None if the instance is not found.

        Raises:
            Exception: If an unexpected error occurs during the operation.
        """
        try:
            # Get instance ID by name
            instance_id = self.get_instance_id_by_name(name)
            if not instance_id:
                print(f"No instance found with the name '{name}'.")
                return None

            # Get instance details by ID
            instance_details = self.get_instance_details_by_id(instance_id)
            if not instance_details:
                print(f"Unable to retrieve details for instance ID '{instance_id}'.")
                return None

            return instance_details

        except ClientError as e:
            print(f"AWS ClientError occurred while fetching instance details by name '{name}': {e}")
            raise

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise


    def get_instance_id_by_name(self, instance_name: str) -> Optional[str]:
        """
        Retrieves the instance ID of an EC2 instance with the specified name.
        
        Args:
            instance_name (str): The name of the EC2 instance to search for.
            
        Returns:
            Optional[str]: The instance ID if found, otherwise None.
            
        Raises:
            NoCredentialsError: If AWS credentials are not found.
            ClientError: If there is an error interacting with the AWS API.
        """
        try:
            # Fetch instance information based on the 'Name' tag
            response = self.ec2.describe_instances(
                Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}]
            )

            # Iterate through the instances to retrieve the instance ID
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    return instance['InstanceId']
            
            # Instance not found
            print(f"No instance found with the name '{instance_name}'")
            return None
        
        except NoCredentialsError:
            print("AWS credentials not found.")
            raise  # Re-raise the exception for the caller to handle
        except ClientError as e:
            print(f"An error occurred while retrieving instance ID: {e}")
            raise  # Re-raise the exception for the caller to handle
    
    def launch_instance_if_not_exists(
            self,
            instance_id: Optional[str], 
            instance_name: str,
            image_id: str = 'ami-012967cc5a8c9f891',
            instance_type: str = 't2.micro',
            key_name: str = None,
            block_device_mappings: Optional[list] = None,
            min_count: int = 1,
            max_count: int = 1,
            volume_size: int = 120,
            delete_on_termination: bool = True
        ) -> Optional[str]:
        """
        Launches an EC2 instance if it does not already exist. If the instance exists, returns the instance ID.
        
        Args:
            instance_id (Optional[str]): The current instance ID (empty if not found).
            instance_name (str): The name of the EC2 instance to assign.
            image_id (str, optional): The Amazon Machine Image (AMI) ID to use for the instance. Default is 'ami-012967cc5a8c9f891'.
            instance_type (str, optional): The instance type. Default is 't2.micro'.
            key_name (str, optional): The name of the key pair to use.
            block_device_mappings (Optional[list], optional): Block device mappings for the instance's storage. Default is None, which will be auto-configured.
            min_count (int, optional): The minimum number of instances to launch. Default is 1.
            max_count (int, optional): The maximum number of instances to launch. Default is 1.
            volume_size (int, optional): The size of the EBS volume in GB. Default is 120 GB.
            delete_on_termination (bool, optional): Whether to delete the EBS volume on instance termination. Default is True.
            
        Returns:
            Optional[str]: The instance ID of the launched or existing instance, or None if an error occurs.
            
        Raises:
            NoCredentialsError: If AWS credentials are not found.
            ClientError: If there is an error interacting with the AWS API.
        """
        if not instance_id:
            try:
                if block_device_mappings is None:
                    block_device_mappings = [
                        {
                            "DeviceName": "/dev/xvda",
                            'Ebs': {
                                'DeleteOnTermination': delete_on_termination,
                                'VolumeSize': volume_size
                            }
                        }
                    ]
                
                # Launch a new EC2 instance
                response = self.ec2.run_instances(
                    ImageId=image_id,
                    MinCount=min_count,
                    MaxCount=max_count,
                    InstanceType=instance_type,
                    KeyName=key_name,
                    BlockDeviceMappings=block_device_mappings
                )
                
                # Retrieve the instance ID from the response
                instance_id = response['Instances'][0]['InstanceId']
                
                # Tag the instance with the provided name
                self.ec2.create_tags(
                    Resources=[instance_id],
                    Tags=[{'Key': 'Name', 'Value': instance_name}]
                )
                print(f"Instance {instance_name} launched with ID: {instance_id}")
            
            except NoCredentialsError:
                print("AWS credentials not found.")
                raise
            except ClientError as e:
                print(f"An error occurred: {e}")
                raise
        else:
            print(f"Instance with ID {instance_id} is already present.")
        
        return instance_id
    
    def create_ec2_instance(
            self,
            instance_name: str,
            instance_id: Optional[str] = None,
            image_id: str = 'ami-012967cc5a8c9f891',
            instance_type: str = 't2.micro',
            key_name: Optional[str] = None,
            volume_size: int = 120
    ) -> Optional[str]:

        """
        Creates an EC2 instance if it does not already exist. If the instance exists, 
        it returns the existing instance ID.

        This function utilizes the `launch_instance_if_not_exists` method to ensure an instance with the 
        given name is created if it does not exist.

        Args:
            instance_name (str): The name of the EC2 instance to assign.
            instance_id (Optional[str], optional): The current instance ID (defaults to None if not found).
            image_id (str, optional): The Amazon Machine Image (AMI) ID to use for the instance. Default is 'ami-012967cc5a8c9f891'.
            instance_type (str, optional): The instance type. Default is 't2.micro'.
            key_name (Optional[str], optional): The name of the key pair to use. Defaults to None, implying no key pair will be used.
            volume_size (int, optional): The size of the EBS volume in GB. Default is 120 GB.

        Returns:
            Optional[str]: The instance ID of the launched or existing instance, or None if an error occurs.
        """
        # By default, instance_id is None, indicating no existing instance. 
        # key_name is also None, indicating no key pair is used.
        return self.launch_instance_if_not_exists(
            instance_id=instance_id,
            instance_name=instance_name,
            image_id=image_id,
            instance_type=instance_type,
            key_name=key_name,
            volume_size=volume_size
        )


    def get_or_create_security_group(self, group_name: str) -> str:
        """
        Retrieves the security group ID for the given security group name.
        If the security group doesn't exist, it creates a new one.

        This function checks for the existence of a security group by its name. 
        If found, it returns the existing security group ID.
        If not found, it creates a new security group and returns the newly created security group ID.

        Args:
            group_name (str): The name of the security group.

        Returns:
            str: The security group ID of the found or newly created security group.

        Raises:
            NoCredentialsError: If AWS credentials are not found.
            ClientError: If there is an error in the AWS API request.
        """
        try:
            response = self.ec2.describe_security_groups(
                Filters=[{'Name': 'group-name', 'Values': [group_name]}]
            )
            
            # Check if the security group exists
            security_group = response.get('SecurityGroups', [])
            if security_group:
                # Security group found, return the ID
                security_group_id = security_group[0]['GroupId']
                print(f"Security group '{group_name}' found with ID: {security_group_id}")
            else:
                # Security group not found, create a new one
                response = self.ec2.create_security_group(
                    GroupName=group_name,
                    Description="Security group for testing"
                )
                security_group_id = response['GroupId']
                print(f"Security group '{group_name}' created with ID: {security_group_id}")
            
            return security_group_id
        except NoCredentialsError:
            print("AWS credentials not found.")
            raise
        except ClientError as e:
            print(f"An error occurred: {e}")
            raise


    def update_security_group(self, group_id: str, protocol: str, port: int, cidr: str) -> bool:
        """
        Updates the security group by adding an ingress rule if it doesn't already exist.

        This function attempts to add an ingress rule for the specified protocol, port, 
        and CIDR block to the given security group.
        If the rule already exists, it handles the `InvalidPermission.Duplicate` error gracefully.
        
        Args:
            group_id (str): The ID of the security group to update.
            protocol (str): The protocol to allow (e.g., 'tcp', 'udp').
            port (int): The port number to allow (e.g., 80 for HTTP).
            cidr (str): The CIDR range to allow access from (e.g., '0.0.0.0/0').

        Returns:
            bool: `True` if the rule was added or already exists, `False` if an error occurred.
        
        Raises:
            NoCredentialsError: If AWS credentials are not found.
            ClientError: If there's an error in the AWS API request.
        """
        try:
            # Attempt to authorize ingress rule
            self.ec2.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=[{
                    'IpProtocol': protocol,
                    'FromPort': port,
                    'ToPort': port,
                    'IpRanges': [{'CidrIp': cidr}]
                }]
            )
            print(f"Ingress rule added to security group {group_id}: {protocol} on port {port} from {cidr}")
            return True

        except ClientError as e:
            # Handle case where the rule already exists
            if e.response['Error']['Code'] == 'InvalidPermission.Duplicate':
                print(f"Ingress rule already exists for security group {group_id}: {protocol} on port {port} from {cidr}")
                return True
            else:
                # Handle other client errors
                print(f"An error occurred while updating security group {group_id}: {e}")
                return False

        except NoCredentialsError:
            print("AWS credentials not found.")
            raise


    def modify_instance_security_group(self, instance_id: str, security_group_id: str) -> None:
        """
        Modifies the security groups associated with an EC2 instance.

        This function allows updating the security groups attached to a running EC2 instance. It replaces the existing security groups with the provided one.

        Args:
            instance_id (str): The ID of the EC2 instance to modify.
            security_group_id (str): The ID of the security group to associate with the instance.

        Returns:
            None: This function does not return any value. It prints status messages based on success or failure.

        Raises:
            NoCredentialsError: If AWS credentials are not found.
            ClientError: If there is an error in the AWS API request.
        """
        try:
            # Modify the security group for the EC2 instance
            self.ec2.modify_instance_attribute(InstanceId=instance_id, Groups=[security_group_id])
            print(f"Security group {security_group_id} applied to instance {instance_id}")
        
        except ClientError as e:
            print(f"Failed to modify instance {instance_id} with security group {security_group_id}: {e}")
            raise
        
        except NoCredentialsError:
            print("AWS credentials not found.")
            raise

    
    def attached_iam_role_to_ec2(self, instance_id: str, role_name: str) -> None:
        """
        Attaches an IAM role to an EC2 instance by creating and associating an instance profile.

        This function performs the following steps:
        1. Retrieves the IAM Role ARN for the specified role.
        2. Ensures the corresponding instance profile exists (or creates it if not).
        3. Attaches the instance profile to the given EC2 instance.

        Args:
            instance_id (str): The ID of the EC2 instance to which the IAM role will be attached.
            role_name (str): The name of the IAM role to attach to the EC2 instance.

        Returns:
            None: This function does not return any value. It prints status messages for each step.

        Raises:
            ClientError: If there is an error interacting with AWS services.
            NoCredentialsError: If AWS credentials are missing.

        Example:
            ec2_manager.attached_iam_role_to_ec2(
                instance_id="i-0123456789abcdef0",
                role_name="MyIAMRole"
            )
        """
        # Step 1: Retrieve IAM Role ARN
        try:
            role_response = self.iam.get_role(RoleName=role_name)
            role_arn = role_response['Role']['Arn']
            print(f"IAM Role '{role_name}' found with ARN: {role_arn}")
        except ClientError as e:
            print(f"Error retrieving IAM Role '{role_name}': {e}")
            raise

        # Step 2: Ensure the instance profile with the same name as the role exists
        instance_profile_name = role_name
        try:
            self.iam.get_instance_profile(InstanceProfileName=instance_profile_name)
            print(f"Instance profile '{instance_profile_name}' already exists.")
        except self.iam.exceptions.NoSuchEntityException:
            # Create the instance profile if it doesn't exist
            try:
                self.iam.create_instance_profile(InstanceProfileName=instance_profile_name)
                print(f"Instance profile '{instance_profile_name}' created.")
                
                # Attach the role to the new instance profile
                self.iam.add_role_to_instance_profile(
                    InstanceProfileName=instance_profile_name,
                    RoleName=role_name
                )
                print(f"Role '{role_name}' added to instance profile '{instance_profile_name}'.")
            except ClientError as e:
                print(f"Error creating or attaching the IAM role: {e}")
                raise

        # Step 3: Attach the instance profile to the specified EC2 instance
        try:
            self.ec2.associate_iam_instance_profile(
                IamInstanceProfile={'Name': instance_profile_name},
                InstanceId=instance_id
            )
            print(f"Instance profile '{instance_profile_name}' attached to EC2 instance '{instance_id}'.")
        except ClientError as e:
            print(f"Error attaching instance profile to EC2 instance '{instance_id}': {e}")
            raise



    def wait_for_status(self, instance_id: str, target_status: str, interval: int = 5, timeout: int = 300) -> None:
        """
        Waits for the EC2 instance to reach the target state within the specified timeout.

        This function continuously checks the status of the EC2 instance until it reaches
        the specified target status or the timeout is reached. It checks the instance status 
        at regular intervals.

        Args:
            instance_id (str): The ID of the EC2 instance whose status is to be monitored.
            target_status (str): The desired status to wait for (e.g., 'running', 'stopped').
            interval (int, optional): The number of seconds to wait between each status check (default is 5).
            timeout (int, optional): The maximum number of seconds to wait for the target status (default is 300).

        Returns:
            None: This function does not return any value. It prints status updates or errors.

        Raises:
            ClientError: If there is an error interacting with AWS services.
            NoCredentialsError: If AWS credentials are missing.
        """
        elapsed_time = 0
        try:
            while elapsed_time < timeout:
                response = self.ec2.describe_instances(InstanceIds=[instance_id])
                status = response['Reservations'][0]['Instances'][0]['State']['Name']
                if status == target_status:
                    print(f"Instance {instance_id} is in '{target_status}' state.")
                    return  # Exit if the instance reaches the target status
                time.sleep(interval)
                elapsed_time += interval
            print(f"Timeout: Instance {instance_id} did not reach '{target_status}' status within {timeout} seconds.")
        except ClientError as e:
            print(f"An error occurred while checking instance {instance_id} status: {e}")
            raise
        except NoCredentialsError:
            print("AWS credentials not found.")
            raise

    def terminate_instance(self, instance_id: str, interval: int = 5, timeout: int = 300) -> None:
        """
        Terminates the specified EC2 instance and waits for it to reach the 'terminated' state.

        Args:
            instance_id (str): The ID of the EC2 instance to be terminated.
            interval (int, optional): The time interval in seconds between status checks (default is 5).
            timeout (int, optional): The maximum time to wait for termination in seconds (default is 300).

        Returns:
            None: This function does not return any value. It will print status updates.

        Raises:
            ClientError: If there is an error with terminating the instance or checking its status.
            NoCredentialsError: If AWS credentials are missing.
        """
        try:
            print(f"Terminating EC2 instance {instance_id}...")
            self.ec2.terminate_instances(InstanceIds=[instance_id])
            return self.wait_for_status(instance_id, 'terminated', interval=interval, timeout=timeout)
        except ClientError as e:
            print(f"An error occurred while terminating instance {instance_id}: {e}")
            raise
        except NoCredentialsError:
            print("AWS credentials not found.")
            raise

    def stop_instance(self, instance_id: str, interval: int = 5, timeout: int = 300) -> None:
        """
        Stops the specified EC2 instance and waits for it to reach the 'stopped' state.

        Args:
            instance_id (str): The ID of the EC2 instance to be stopped.
            interval (int, optional): The time interval in seconds between status checks (default is 5).
            timeout (int, optional): The maximum time to wait for stopping the instance in seconds (default is 300).

        Returns:
            None: This function does not return any value. It will print status updates.

        Raises:
            ClientError: If there is an error with stopping the instance or checking its status.
            NoCredentialsError: If AWS credentials are missing.
        """
        try:
            print(f"Stopping EC2 instance {instance_id}...")
            self.ec2.stop_instances(InstanceIds=[instance_id])
            return self.wait_for_status(instance_id, 'stopped', interval=interval, timeout=timeout)
        except ClientError as e:
            print(f"An error occurred while stopping instance {instance_id}: {e}")
            raise
        except NoCredentialsError:
            print("AWS credentials not found.")
            raise

    def start_instance(self, instance_id: str, interval: int = 5, timeout: int = 300) -> None:
        """
        Starts the specified EC2 instance and waits for it to reach the 'running' state.

        Args:
            instance_id (str): The ID of the EC2 instance to be started.
            interval (int, optional): The time interval in seconds between status checks (default is 5).
            timeout (int, optional): The maximum time to wait for the instance to be running in seconds (default is 300).

        Returns:
            None: This function does not return any value. It will print status updates.

        Raises:
            ClientError: If there is an error with starting the instance or checking its status.
            NoCredentialsError: If AWS credentials are missing.
        """
        try:
            print(f"Starting EC2 instance {instance_id}...")
            self.ec2.start_instances(InstanceIds=[instance_id])
            return self.wait_for_status(instance_id, 'running', interval=interval, timeout=timeout)
        except ClientError as e:
            print(f"An error occurred while starting instance {instance_id}: {e}")
            raise
        except NoCredentialsError:
            print("AWS credentials not found.")
            raise

    def get_instance_public_ip(self, instance_id: str) -> Optional[str]:
        """
        Retrieves the public IP address of an EC2 instance.

        Args:
            instance_id (str): The ID of the EC2 instance whose public IP address is to be retrieved.

        Returns:
            Optional[str]: The public IP address of the instance if available, otherwise None.
            
        Raises:
            ClientError: If there is an issue with the AWS EC2 API call.
            NoCredentialsError: If AWS credentials are missing.
        """
        try:
            response = self.ec2.describe_instances(InstanceIds=[instance_id])
            public_ip = response['Reservations'][0]['Instances'][0].get('PublicIpAddress')

            if public_ip:
                print(f"Instance {instance_id} has public IP: {public_ip}")
            else:
                print(f"Instance {instance_id} does not have a public IP address assigned.")
            return public_ip
        except ClientError as e:
            print(f"An error occurred while retrieving public IP for instance {instance_id}: {e}")
            raise
        except NoCredentialsError:
            print("AWS credentials not found.")
            raise
    
    def create_key_pair(
    self, 
    key_name: str, 
    file_path: str, 
    return_full_path: bool = False
    ) -> str | None:
        """
        Creates a new EC2 key pair and saves the private key material to a .pem file 
        with the same name as the key pair.

        Args:
            key_name (str): The name for the new key pair and the .pem file.
            file_path (str): The directory path where the .pem file will be stored.
            return_full_path (bool, optional): If True, returns the full path of the saved .pem file. Defaults to False.

        Returns:
            str | None: The full path of the saved .pem file if return_full_path=True; otherwise, returns None.

        Raises:
            FileExistsError: If the .pem file already exists at the specified location.
            ClientError: If the AWS EC2 create_key_pair API call fails.
            NoCredentialsError: If AWS credentials are missing.
        """
        try:
            # Prepare the full file path using the key_name for the file name
            full_path = os.path.join(file_path, f"{key_name}.pem")
            
            # Check if the file already exists
            if os.path.exists(full_path):
                raise FileExistsError(f"The file '{full_path}' already exists. Operation aborted to avoid overwriting.")
            
            # Create the key pair using AWS EC2 API
            print(f"Creating key pair '{key_name}'...")
            response = self.ec2.create_key_pair(KeyName=key_name)
            
            # Save the private key material to the file
            os.makedirs(file_path, exist_ok=True)  # Ensure the directory exists
            with open(full_path, 'w') as file:
                file.write(response['KeyMaterial'])
            os.chmod(full_path, 0o400)  # Secure the file by setting permissions
            
            print(f"Key pair '{key_name}' created and saved to '{full_path}'.")
            
            # Return the full path only if requested
            if return_full_path:
                return full_path

        except FileExistsError as e:
            print(e)
        except ClientError as e:
            print(f"An error occurred while creating key pair '{key_name}': {e}")
            raise
        except NoCredentialsError:
            print("AWS credentials not found.")
            raise
    
    def get_instances_by_state(self, state: str) -> List[dict]:
        """
        Retrieves EC2 instances by their state.

        Args:
            state (str): The state of the instances to retrieve (e.g., 'running', 'stopped').

        Returns:
            List[dict]: A list of instances in the specified state.
        """
        try:
            instances = self.list_all_instances(get_count_message=False)
            return [instance for instance in instances if instance['State'] == state]
        except Exception as e:
            print(f"Error filtering instances by state '{state}': {e}")
            raise

