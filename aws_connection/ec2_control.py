# aws_connection/ec2_control.py

import boto3

def list_instances(session):
    """
    List all EC2 instances in the connected AWS account.

    Parameters:
    - session (boto3.Session): Authenticated AWS session object.

    Returns:
    - instances (list): A list of instance information dictionaries.
    """
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
                "PrivateIpAddress": instance.get('PrivateIpAddress')
            })

    return instances


def start_instance(session, instance_id):
    """
    Start an EC2 instance.

    Parameters:
    - session (boto3.Session): Authenticated AWS session object.
    - instance_id (str): The ID of the instance to start.

    Returns:
    - response (dict): Response from the start operation.
    """
    ec2_client = session.client('ec2')
    response = ec2_client.start_instances(InstanceIds=[instance_id])
    return response


def stop_instance(session, instance_id):
    """
    Stop an EC2 instance.

    Parameters:
    - session (boto3.Session): Authenticated AWS session object.
    - instance_id (str): The ID of the instance to stop.

    Returns:
    - response (dict): Response from the stop operation.
    """
    ec2_client = session.client('ec2')
    response = ec2_client.stop_instances(InstanceIds=[instance_id])
    return response


def reboot_instance(session, instance_id):
    """
    Reboot an EC2 instance.

    Parameters:
    - session (boto3.Session): Authenticated AWS session object.
    - instance_id (str): The ID of the instance to reboot.

    Returns:
    - response (dict): Response from the reboot operation.
    """
    ec2_client = session.client('ec2')
    response = ec2_client.reboot_instances(InstanceIds=[instance_id])
    return response


def get_instance_network_info(session, instance_id):
    """
    Retrieve network information for a specific EC2 instance.

    Parameters:
    - session (boto3.Session): Authenticated AWS session object.
    - instance_id (str): The ID of the instance to retrieve info for.

    Returns:
    - network_info (dict): Dictionary containing network information.
    """
    ec2_client = session.client('ec2')
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance = response['Reservations'][0]['Instances'][0]

    network_info = {
        "InstanceId": instance['InstanceId'],
        "PublicIpAddress": instance.get('PublicIpAddress'),
        "PrivateIpAddress": instance.get('PrivateIpAddress'),
        "PublicDnsName": instance.get('PublicDnsName'),
        "PrivateDnsName": instance.get('PrivateDnsName'),
        "ElasticIp": instance.get('ElasticIp', {}).get('PublicIp')
    }

    return network_info
