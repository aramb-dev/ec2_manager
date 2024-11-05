import customtkinter as ctk
import tkinter as tk
import os
from aws_connection import setup_aws_session, list_instances, start_instance, stop_instance, reboot_instance, get_instance_network_info
from utils import log_and_display, validate_aws_credentials, format_instance_info
from cryptography.fernet import Fernet

class EC2ManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EC2 Manager")
        self.minsize(600, 400)
        self.aws_session = None
        self.credentials_encrypted = "credentials.enc"

        # Generate or load encryption key
        self.encryption_key = self.load_encryption_key()

        # Initialize login screen
        self.init_login_screen()

    def load_encryption_key(self):
        """
        Generate/load encryption key for storing AWS credentials.
        """
        key_file = "key.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as keyfile:
                return keyfile.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as keyfile:
                keyfile.write(key)
            return key

    def encrypt_credentials(self, access_key, secret_key, region):
        """
        Encrypt AWS credentials for secure storage.
        """
        cipher = Fernet(self.encryption_key)
        credentials = f"{access_key},{secret_key},{region}".encode()
        encrypted_credentials = cipher.encrypt(credentials)
        with open(self.credentials_encrypted, "wb") as enc_file:
            enc_file.write(encrypted_credentials)

    def decrypt_credentials(self):
        """
        Decrypt and retrieve stored AWS credentials.
        """
        if os.path.exists(self.credentials_encrypted):
            cipher = Fernet(self.encryption_key)
            with open(self.credentials_encrypted, "rb") as enc_file:
                decrypted_credentials = cipher.decrypt(enc_file.read()).decode()
                return decrypted_credentials.split(",")
        return None, None, None

    def init_login_screen(self):
        """
        Initialize login screen for entering AWS credentials.
        """
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # AWS Access Key
        self.access_key_label = ctk.CTkLabel(self, text="AWS Access Key:")
        self.access_key_label.pack(pady=5)
        self.access_key_entry = ctk.CTkEntry(self)
        self.access_key_entry.pack(pady=5)

        # AWS Secret Key
        self.secret_key_label = ctk.CTkLabel(self, text="AWS Secret Key:")
        self.secret_key_label.pack(pady=5)
        self.secret_key_entry = ctk.CTkEntry(self, show="*")
        self.secret_key_entry.pack(pady=5)

        # AWS Region
        self.region_label = ctk.CTkLabel(self, text="AWS Region:")
        self.region_label.pack(pady=5)
        self.region_entry = ctk.CTkEntry(self)
        self.region_entry.pack(pady=5)

        # Connect Button
        self.connect_button = ctk.CTkButton(self, text="Connect to AWS", command=self.connect_aws)
        self.connect_button.pack(pady=10)

        # Load credentials if available
        access_key, secret_key, region = self.decrypt_credentials()
        if access_key and secret_key and region:
            self.access_key_entry.insert(0, access_key)
            self.secret_key_entry.insert(0, secret_key)
            self.region_entry.insert(0, region)

    def connect_aws(self):
        """
        Connect to AWS using provided or stored credentials and region.
        """
        aws_access_key = self.access_key_entry.get().strip()
        aws_secret_key = self.secret_key_entry.get().strip()
        region = self.region_entry.get().strip()

        if validate_aws_credentials(aws_access_key, aws_secret_key, region):
            self.aws_session = setup_aws_session(aws_access_key, aws_secret_key, region)
            if self.aws_session:
                log_and_display(self.instance_info_text, "Connected to AWS")
                self.encrypt_credentials(aws_access_key, aws_secret_key, region)  # Save encrypted credentials
                self.show_instance_management_screen()
            else:
                log_and_display(self.instance_info_text, "Failed to connect to AWS. Check credentials.", "error")
        else:
            log_and_display(self.instance_info_text, "Invalid AWS credentials provided.", "warning")

    def show_instance_management_screen(self):
        """
        Show the instance management screen and add a Logout button.
        """
        for widget in self.winfo_children():
            widget.destroy()

        # Add Logout Button
        self.logout_button = ctk.CTkButton(self, text="Logout", command=self.logout)
        self.logout_button.pack(pady=10)

        # Instance list and management buttons (same as before)
        # ...

    def logout(self):
        """
        Clear AWS session and return to login screen.
        """
        self.aws_session = None
        self.init_login_screen()
