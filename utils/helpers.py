# utils/helpers.py

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_and_display(text_widget, message, level="info"):
    """
    Logs a message and displays it in the provided text widget.

    Parameters:
    - text_widget (customtkinter.CTkTextbox): The widget where the message will be displayed.
    - message (str): The message to log and display.
    - level (str): The logging level ('info', 'warning', 'error').
    """
    if level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)

    text_widget.insert("end", f"{message}\n")
    text_widget.see("end")


def validate_aws_credentials(access_key, secret_key, region):
    """
    Validates AWS credentials input by checking if they are non-empty strings.

    Parameters:
    - access_key (str): AWS access key.
    - secret_key (str): AWS secret key.
    - region (str): AWS region.

    Returns:
    - (bool): True if all inputs are valid, otherwise False.
    """
    if not access_key or not secret_key or not region:
        return False
    return True


def format_instance_info(instance_info):
    """
    Formats instance information for display in the GUI.

    Parameters:
    - instance_info (dict): Dictionary containing instance details.

    Returns:
    - formatted_info (str): Formatted string of instance details.
    """
    formatted_info = (
        f"Instance ID: {instance_info.get('InstanceId')}\n"
        f"State: {instance_info.get('State', 'N/A')}\n"
        f"Instance Type: {instance_info.get('InstanceType', 'N/A')}\n"
        f"Public IP: {instance_info.get('PublicIpAddress', 'N/A')}\n"
        f"Private IP: {instance_info.get('PrivateIpAddress', 'N/A')}\n"
        f"Public DNS: {instance_info.get('PublicDnsName', 'N/A')}\n"
        f"Private DNS: {instance_info.get('PrivateDnsName', 'N/A')}\n"
    )
    return formatted_info
