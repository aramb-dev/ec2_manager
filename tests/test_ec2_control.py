# tests/test_ec2_control.py

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from aws_connection.ec2_control import list_instances, start_instance, stop_instance, reboot_instance, get_instance_network_info
from botocore.exceptions import ClientError


class TestEC2Control(unittest.TestCase):
    """Test suite for EC2 control operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_session = MagicMock()
        self.mock_ec2_client = MagicMock()
        self.mock_session.client.return_value = self.mock_ec2_client

    def test_list_instances_success(self):
        """Test successful instance listing."""
        # Mock describe_instances response
        self.mock_ec2_client.describe_instances.return_value = {
            'Reservations': [
                {
                    'Instances': [
                        {
                            'InstanceId': 'i-1234567890abcdef0',
                            'State': {'Name': 'running'},
                            'InstanceType': 't2.micro',
                            'PublicIpAddress': '54.123.45.67',
                            'PrivateIpAddress': '10.0.1.23',
                            'Tags': [{'Key': 'Name', 'Value': 'TestInstance'}]
                        }
                    ]
                }
            ]
        }

        result = list_instances(self.mock_session)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['InstanceId'], 'i-1234567890abcdef0')
        self.assertEqual(result[0]['State'], 'running')
        self.assertEqual(result[0]['InstanceType'], 't2.micro')
        self.assertIn('Tags', result[0])

    def test_list_instances_multiple(self):
        """Test listing multiple instances."""
        self.mock_ec2_client.describe_instances.return_value = {
            'Reservations': [
                {
                    'Instances': [
                        {
                            'InstanceId': 'i-1111111111111111',
                            'State': {'Name': 'running'},
                            'InstanceType': 't2.micro',
                            'PublicIpAddress': '54.1.1.1',
                            'PrivateIpAddress': '10.0.1.1',
                            'Tags': []
                        },
                        {
                            'InstanceId': 'i-2222222222222222',
                            'State': {'Name': 'stopped'},
                            'InstanceType': 't2.small',
                            'Tags': []
                        }
                    ]
                }
            ]
        }

        result = list_instances(self.mock_session)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['InstanceId'], 'i-1111111111111111')
        self.assertEqual(result[1]['InstanceId'], 'i-2222222222222222')

    def test_list_instances_client_error(self):
        """Test listing instances with client error."""
        error_response = {
            'Error': {
                'Code': 'UnauthorizedOperation',
                'Message': 'You are not authorized to perform this operation.'
            }
        }
        self.mock_ec2_client.describe_instances.side_effect = ClientError(error_response, 'DescribeInstances')

        result = list_instances(self.mock_session)

        self.assertIsNone(result)

    def test_start_instance_success(self):
        """Test successful instance start."""
        self.mock_ec2_client.start_instances.return_value = {
            'StartingInstances': [
                {
                    'InstanceId': 'i-1234567890abcdef0',
                    'CurrentState': {'Name': 'pending'},
                    'PreviousState': {'Name': 'stopped'}
                }
            ]
        }

        result = start_instance(self.mock_session, 'i-1234567890abcdef0')

        self.assertTrue(result)
        self.mock_ec2_client.start_instances.assert_called_once_with(InstanceIds=['i-1234567890abcdef0'])

    def test_start_instance_client_error(self):
        """Test starting instance with client error."""
        error_response = {
            'Error': {
                'Code': 'InvalidInstanceID.NotFound',
                'Message': 'The instance ID does not exist'
            }
        }
        self.mock_ec2_client.start_instances.side_effect = ClientError(error_response, 'StartInstances')

        result = start_instance(self.mock_session, 'i-invalid')

        self.assertFalse(result)

    def test_stop_instance_success(self):
        """Test successful instance stop."""
        self.mock_ec2_client.stop_instances.return_value = {
            'StoppingInstances': [
                {
                    'InstanceId': 'i-1234567890abcdef0',
                    'CurrentState': {'Name': 'stopping'},
                    'PreviousState': {'Name': 'running'}
                }
            ]
        }

        result = stop_instance(self.mock_session, 'i-1234567890abcdef0')

        self.assertTrue(result)
        self.mock_ec2_client.stop_instances.assert_called_once_with(InstanceIds=['i-1234567890abcdef0'])

    def test_stop_instance_client_error(self):
        """Test stopping instance with client error."""
        error_response = {
            'Error': {
                'Code': 'IncorrectInstanceState',
                'Message': 'The instance is not in a state from which it can be stopped.'
            }
        }
        self.mock_ec2_client.stop_instances.side_effect = ClientError(error_response, 'StopInstances')

        result = stop_instance(self.mock_session, 'i-1234567890abcdef0')

        self.assertFalse(result)

    def test_reboot_instance_success(self):
        """Test successful instance reboot."""
        self.mock_ec2_client.reboot_instances.return_value = {}

        result = reboot_instance(self.mock_session, 'i-1234567890abcdef0')

        self.assertTrue(result)
        self.mock_ec2_client.reboot_instances.assert_called_once_with(InstanceIds=['i-1234567890abcdef0'])

    def test_reboot_instance_client_error(self):
        """Test rebooting instance with client error."""
        error_response = {
            'Error': {
                'Code': 'InvalidInstanceID.NotFound',
                'Message': 'The instance ID does not exist'
            }
        }
        self.mock_ec2_client.reboot_instances.side_effect = ClientError(error_response, 'RebootInstances')

        result = reboot_instance(self.mock_session, 'i-invalid')

        self.assertFalse(result)

    def test_get_instance_network_info_success(self):
        """Test successful network info retrieval."""
        self.mock_ec2_client.describe_instances.return_value = {
            'Reservations': [
                {
                    'Instances': [
                        {
                            'InstanceId': 'i-1234567890abcdef0',
                            'State': {'Name': 'running'},
                            'InstanceType': 't2.micro',
                            'PublicIpAddress': '54.123.45.67',
                            'PrivateIpAddress': '10.0.1.23',
                            'PublicDnsName': 'ec2-54-123-45-67.compute-1.amazonaws.com',
                            'PrivateDnsName': 'ip-10-0-1-23.ec2.internal'
                        }
                    ]
                }
            ]
        }

        result = get_instance_network_info(self.mock_session, 'i-1234567890abcdef0')

        self.assertIsNotNone(result)
        self.assertEqual(result['InstanceId'], 'i-1234567890abcdef0')
        self.assertEqual(result['State'], 'running')
        self.assertEqual(result['PublicIpAddress'], '54.123.45.67')
        self.assertEqual(result['PrivateIpAddress'], '10.0.1.23')

    def test_get_instance_network_info_client_error(self):
        """Test getting network info with client error."""
        error_response = {
            'Error': {
                'Code': 'InvalidInstanceID.NotFound',
                'Message': 'The instance ID does not exist'
            }
        }
        self.mock_ec2_client.describe_instances.side_effect = ClientError(error_response, 'DescribeInstances')

        result = get_instance_network_info(self.mock_session, 'i-invalid')

        self.assertIsNone(result)

    def test_get_instance_network_info_no_public_ip(self):
        """Test getting network info for instance without public IP."""
        self.mock_ec2_client.describe_instances.return_value = {
            'Reservations': [
                {
                    'Instances': [
                        {
                            'InstanceId': 'i-1234567890abcdef0',
                            'State': {'Name': 'running'},
                            'InstanceType': 't2.micro',
                            'PrivateIpAddress': '10.0.1.23',
                            'PrivateDnsName': 'ip-10-0-1-23.ec2.internal'
                        }
                    ]
                }
            ]
        }

        result = get_instance_network_info(self.mock_session, 'i-1234567890abcdef0')

        self.assertIsNotNone(result)
        self.assertEqual(result['InstanceId'], 'i-1234567890abcdef0')
        self.assertIsNone(result['PublicIpAddress'])
        self.assertEqual(result['PrivateIpAddress'], '10.0.1.23')


if __name__ == '__main__':
    unittest.main()
