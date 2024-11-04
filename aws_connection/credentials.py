# aws_connection/credentials.py

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


def setup_aws_session(aws_access_key: str, aws_secret_key: str, region: str):
    """
    Set up an AWS session using the provided credentials and region.

    Parameters:
    - aws_access_key (str): AWS access key ID.
    - aws_secret_key (str): AWS secret access key.
    - region (str): AWS region.

    Returns:
    - session (boto3.Session): Authenticated AWS session object, or None if invalid credentials.
    """
    try:
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region,
        )

        # Test the connection by making a simple API call
        ec2_client = session.client("ec2")
        ec2_client.describe_regions()  # Check if credentials and region are valid

        print("AWS session successfully created.")
        return session

    except NoCredentialsError:
        print("No AWS credentials were provided.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials were provided.")
    except Exception as e:
        print(f"An error occurred while setting up AWS session: {e}")

    return None
