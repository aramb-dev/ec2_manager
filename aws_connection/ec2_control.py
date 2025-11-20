# aws_connection/ec2_control.py

import boto3
from botocore.exceptions import ClientError, BotoCoreError

def list_instances(session):
    """
    List all EC2 instances in the connected AWS account.

    Parameters:
    - session (boto3.Session): Authenticated AWS session object.

    Returns:
    - instances (list): A list of instance information dictionaries, or None if error.
    """
    try:
        ec2_client = session.client('ec2')
        response = ec2_client.describe_instances()
        instances = []

        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    "InstanceId": instance['InstanceId'],
                    "State": instance['State']['Name'],
                    "InstanceType": instance['InstanceType'],
                    "PublicIpAddress": instance.get('PublicIpAddress'),
                    "PrivateIpAddress": instance.get('PrivateIpAddress'),
                    "Tags": instance.get('Tags', [])
                })

        return instances
    except ClientError as e:
        print(f"AWS API error listing instances: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        print(f"Unexpected error listing instances: {str(e)}")
        return None


def start_instance(session, instance_id):
    """
    Start an EC2 instance.

    Parameters:
    - session (boto3.Session): Authenticated AWS session object.
    - instance_id (str): The ID of the instance to start.

    Returns:
    - bool: True if successful, False otherwise.
    """
    try:
        ec2_client = session.client('ec2')
        ec2_client.start_instances(InstanceIds=[instance_id])
        return True
    except ClientError as e:
        print(f"AWS API error starting instance {instance_id}: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"Unexpected error starting instance {instance_id}: {str(e)}")
        return False


def stop_instance(session, instance_id):
    """
    Stop an EC2 instance.

    Parameters:
    - session (boto3.Session): Authenticated AWS session object.
    - instance_id (str): The ID of the instance to stop.

    Returns:
    - bool: True if successful, False otherwise.
    """
    try:
        ec2_client = session.client('ec2')
        ec2_client.stop_instances(InstanceIds=[instance_id])
        return True
    except ClientError as e:
        print(f"AWS API error stopping instance {instance_id}: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"Unexpected error stopping instance {instance_id}: {str(e)}")
        return False


def reboot_instance(session, instance_id):
    """
    Reboot an EC2 instance.

    Parameters:
    - session (boto3.Session): Authenticated AWS session object.
    - instance_id (str): The ID of the instance to reboot.

    Returns:
    - bool: True if successful, False otherwise.
    """
    try:
        ec2_client = session.client('ec2')
        ec2_client.reboot_instances(InstanceIds=[instance_id])
        return True
    except ClientError as e:
        print(f"AWS API error rebooting instance {instance_id}: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"Unexpected error rebooting instance {instance_id}: {str(e)}")
        return False


def get_instance_network_info(session, instance_id):
    """
    Retrieve network information for a specific EC2 instance.

    Parameters:
    - session (boto3.Session): Authenticated AWS session object.
    - instance_id (str): The ID of the instance to retrieve info for.

    Returns:
    - network_info (dict): Dictionary containing network information, or None if error.
    """
    try:
        ec2_client = session.client('ec2')
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]

        network_info = {
            "InstanceId": instance['InstanceId'],
            "State": instance['State']['Name'],
            "InstanceType": instance['InstanceType'],
            "PublicIpAddress": instance.get('PublicIpAddress'),
            "PrivateIpAddress": instance.get('PrivateIpAddress'),
            "PublicDnsName": instance.get('PublicDnsName'),
            "PrivateDnsName": instance.get('PrivateDnsName'),
            "ElasticIp": instance.get('ElasticIp', {}).get('PublicIp')
        }

        return network_info
    except ClientError as e:
        print(f"AWS API error getting network info for instance {instance_id}: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        print(f"Unexpected error getting network info for instance {instance_id}: {str(e)}")
        return None
