# tests/test_credentials.py

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from aws_connection.credentials import setup_aws_session
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError


class TestCredentials(unittest.TestCase):
    """Test suite for AWS credentials and session setup."""

    @patch('aws_connection.credentials.boto3.Session')
    def test_setup_aws_session_success(self, mock_session_class):
        """Test successful AWS session setup."""
        # Mock the session and client
        mock_session = MagicMock()
        mock_ec2_client = MagicMock()
        mock_session.client.return_value = mock_ec2_client
        mock_session_class.return_value = mock_session

        # Mock describe_regions to succeed
        mock_ec2_client.describe_regions.return_value = {"Regions": []}

        # Call the function
        result = setup_aws_session("AKIAIOSFODNN7EXAMPLE", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", "us-east-1")

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result, mock_session)
        mock_session_class.assert_called_once_with(
            aws_access_key_id="AKIAIOSFODNN7EXAMPLE",
            aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            region_name="us-east-1"
        )
        mock_session.client.assert_called_once_with("ec2")
        mock_ec2_client.describe_regions.assert_called_once()

    @patch('aws_connection.credentials.boto3.Session')
    def test_setup_aws_session_no_credentials_error(self, mock_session_class):
        """Test session setup with no credentials."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.client.side_effect = NoCredentialsError()

        with self.assertRaises(Exception) as context:
            setup_aws_session("", "", "us-east-1")

        self.assertIn("AWS credentials are missing", str(context.exception))

    @patch('aws_connection.credentials.boto3.Session')
    def test_setup_aws_session_partial_credentials_error(self, mock_session_class):
        """Test session setup with partial credentials."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.client.side_effect = PartialCredentialsError(provider='test', cred_var='test')

        with self.assertRaises(Exception) as context:
            setup_aws_session("AKIAIOSFODNN7EXAMPLE", "", "us-east-1")

        self.assertIn("Incomplete credentials", str(context.exception))

    @patch('aws_connection.credentials.boto3.Session')
    def test_setup_aws_session_invalid_credentials(self, mock_session_class):
        """Test session setup with invalid credentials."""
        mock_session = MagicMock()
        mock_ec2_client = MagicMock()
        mock_session.client.return_value = mock_ec2_client
        mock_session_class.return_value = mock_session

        # Mock ClientError for invalid credentials
        error_response = {
            'Error': {
                'Code': 'InvalidClientTokenId',
                'Message': 'The security token included in the request is invalid.'
            }
        }
        mock_ec2_client.describe_regions.side_effect = ClientError(error_response, 'DescribeRegions')

        with self.assertRaises(Exception) as context:
            setup_aws_session("INVALIDKEY", "INVALIDSECRET", "us-east-1")

        self.assertIn("Invalid AWS credentials", str(context.exception))

    @patch('aws_connection.credentials.boto3.Session')
    def test_setup_aws_session_region_not_enabled(self, mock_session_class):
        """Test session setup with region not enabled."""
        mock_session = MagicMock()
        mock_ec2_client = MagicMock()
        mock_session.client.return_value = mock_ec2_client
        mock_session_class.return_value = mock_session

        # Mock ClientError for region not enabled
        error_response = {
            'Error': {
                'Code': 'OptInRequired',
                'Message': 'You are not authorized to use this region.'
            }
        }
        mock_ec2_client.describe_regions.side_effect = ClientError(error_response, 'DescribeRegions')

        with self.assertRaises(Exception) as context:
            setup_aws_session("AKIAIOSFODNN7EXAMPLE", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", "ap-east-1")

        self.assertIn("not enabled for your account", str(context.exception))

    @patch('aws_connection.credentials.boto3.Session')
    def test_setup_aws_session_generic_client_error(self, mock_session_class):
        """Test session setup with generic AWS client error."""
        mock_session = MagicMock()
        mock_ec2_client = MagicMock()
        mock_session.client.return_value = mock_ec2_client
        mock_session_class.return_value = mock_session

        # Mock generic ClientError
        error_response = {
            'Error': {
                'Code': 'SomeOtherError',
                'Message': 'Some other error occurred.'
            }
        }
        mock_ec2_client.describe_regions.side_effect = ClientError(error_response, 'DescribeRegions')

        with self.assertRaises(Exception) as context:
            setup_aws_session("AKIAIOSFODNN7EXAMPLE", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", "us-east-1")

        self.assertIn("AWS Error", str(context.exception))


if __name__ == '__main__':
    unittest.main()
