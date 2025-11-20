# aws_connection/credentials.py

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import logging

logger = logging.getLogger(__name__)


def setup_aws_session(aws_access_key: str, aws_secret_key: str, region: str):
    """
    Set up an AWS session using the provided credentials and region.

    Parameters:
    - aws_access_key (str): AWS access key ID.
    - aws_secret_key (str): AWS secret access key.
    - region (str): AWS region.

    Returns:
    - session (boto3.Session): Authenticated AWS session object, or None if invalid credentials.

    Raises:
    - Exception: With user-friendly error message if connection fails.
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

        logger.info("AWS session successfully created")
        return session

    except NoCredentialsError:
        logger.error("No AWS credentials provided")
        raise Exception("AWS credentials are missing. Please enter your Access Key and Secret Key.")
    except PartialCredentialsError:
        logger.error("Incomplete AWS credentials")
        raise Exception("Incomplete credentials. Please ensure both Access Key and Secret Key are provided.")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UnauthorizedOperation' or error_code == 'InvalidClientTokenId':
            logger.error(f"Invalid AWS credentials: {error_code}")
            raise Exception("Invalid AWS credentials. Please verify your Access Key and Secret Key are correct.")
        elif error_code == 'OptInRequired':
            logger.error(f"Region not enabled: {region}")
            raise Exception(f"The region '{region}' is not enabled for your account. Please choose a different region.")
        else:
            logger.error(f"AWS API error: {error_code}")
            raise Exception(f"AWS Error: {e.response['Error']['Message']}")
    except Exception as e:
        logger.error(f"Unexpected error setting up AWS session: {str(e)}")
        raise Exception(f"Connection failed: {str(e)}")
