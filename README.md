# EC2 Manager
This is a Python script/app which aids you to lightly manage your ec2 instances in your AWS account.

## Video DEMO:
https://github.com/user-attachments/assets/63e3ec44-8ff0-4b52-b0b1-98e1f83bc4e3

## Prerequisites

- Python 3.6 or higher
- AWS credentials (Access Key ID and Secret Access Key)

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/ec2_manager.git
    cd ec2_manager
    ```

2. Create a virtual environment and activate it:

    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```


## Running the Application

1. Run the application:

    ```sh
    python main.py
    ```

2. Enter your AWS Access Key, Secret Key, and Region in the application window and click "Connect to AWS".

3. Once connected, you can manage your EC2 instances from the application.

## Usage

- **Connect to AWS**: Enter your AWS credentials and region, then click "Connect to AWS".
- **Manage Instances**: After connecting, you can view, start, stop, and reboot your EC2 instances.
- **View Instance Info**: Select an instance from the list to view detailed information, including instance type, network info (IP addresses, hostname, etc.), status, and whether a private key is attached.

If you find any issues, please [open an issue on GitHub](https://github.com/aramb-dev/ec2-manager/issues).

If you have any suggestions, please [open a PR on GitHub](https://github.com/aramb-dev/ec2-manager/pulls).
