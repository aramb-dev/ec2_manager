# tests/test_helpers.py

import unittest
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import validate_aws_credentials, format_instance_info


class TestHelpers(unittest.TestCase):
    """Test suite for utility helper functions."""

    def test_validate_aws_credentials_valid(self):
        """Test that valid credentials return True."""
        result = validate_aws_credentials("AKIAIOSFODNN7EXAMPLE", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", "us-east-1")
        self.assertTrue(result)

    def test_validate_aws_credentials_empty_access_key(self):
        """Test that empty access key returns False."""
        result = validate_aws_credentials("", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", "us-east-1")
        self.assertFalse(result)

    def test_validate_aws_credentials_empty_secret_key(self):
        """Test that empty secret key returns False."""
        result = validate_aws_credentials("AKIAIOSFODNN7EXAMPLE", "", "us-east-1")
        self.assertFalse(result)

    def test_validate_aws_credentials_empty_region(self):
        """Test that empty region returns False."""
        result = validate_aws_credentials("AKIAIOSFODNN7EXAMPLE", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", "")
        self.assertFalse(result)

    def test_validate_aws_credentials_all_empty(self):
        """Test that all empty credentials return False."""
        result = validate_aws_credentials("", "", "")
        self.assertFalse(result)

    def test_validate_aws_credentials_whitespace_only(self):
        """
        Test that whitespace-only credentials return True.

        Note: validate_aws_credentials() doesn't strip whitespace - it only checks
        for empty strings. The GUI layer (main_window.py) calls .strip() before
        passing credentials to this function, so whitespace-only strings are
        caught at the GUI level.
        """
        result = validate_aws_credentials("   ", "   ", "   ")
        self.assertTrue(result)  # Whitespace strings are truthy in Python

    def test_format_instance_info_complete(self):
        """Test formatting complete instance info."""
        instance_info = {
            "InstanceId": "i-1234567890abcdef0",
            "State": "running",
            "InstanceType": "t2.micro",
            "PublicIpAddress": "54.123.45.67",
            "PrivateIpAddress": "10.0.1.23",
            "PublicDnsName": "ec2-54-123-45-67.compute-1.amazonaws.com",
            "PrivateDnsName": "ip-10-0-1-23.ec2.internal"
        }

        result = format_instance_info(instance_info)

        self.assertIn("i-1234567890abcdef0", result)
        self.assertIn("running", result)
        self.assertIn("t2.micro", result)
        self.assertIn("54.123.45.67", result)
        self.assertIn("10.0.1.23", result)
        self.assertIn("ec2-54-123-45-67.compute-1.amazonaws.com", result)
        self.assertIn("ip-10-0-1-23.ec2.internal", result)

    def test_format_instance_info_partial(self):
        """Test formatting instance info with missing fields."""
        instance_info = {
            "InstanceId": "i-1234567890abcdef0",
            "State": None,
            "InstanceType": None,
            "PublicIpAddress": None,
            "PrivateIpAddress": "10.0.1.23"
        }

        result = format_instance_info(instance_info)

        self.assertIn("i-1234567890abcdef0", result)
        self.assertIn("N/A", result)  # Missing fields should show as N/A
        self.assertIn("10.0.1.23", result)

    def test_format_instance_info_minimal(self):
        """Test formatting instance info with only InstanceId."""
        instance_info = {
            "InstanceId": "i-1234567890abcdef0"
        }

        result = format_instance_info(instance_info)

        self.assertIn("i-1234567890abcdef0", result)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


if __name__ == '__main__':
    unittest.main()
