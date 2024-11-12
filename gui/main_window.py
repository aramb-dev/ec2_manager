# gui/main_window.py

import customtkinter as ctk
import tkinter as tk
from aws_connection import setup_aws_session, list_instances, start_instance, stop_instance, reboot_instance, get_instance_network_info
from utils import log_and_display, validate_aws_credentials, format_instance_info

class EC2ManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EC2 Manager")
        self.geometry("600x400")
        self.aws_session = None

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

        # Instance Info Textbox
        self.instance_info_text = ctk.CTkTextbox(self, width=400, height=200)
        self.instance_info_text.pack(pady=10)

    def connect_aws(self):
        aws_access_key = self.access_key_entry.get().strip()
        aws_secret_key = self.secret_key_entry.get().strip()
        region = self.region_entry.get().strip()

        if validate_aws_credentials(aws_access_key, aws_secret_key, region):
            try:
                self.aws_session = setup_aws_session(aws_access_key, aws_secret_key, region)
                if self.aws_session:
                    log_and_display(self.instance_info_text, "Connected to AWS")
                    self.show_instance_management_screen()
                else:
                    log_and_display(self.instance_info_text, "Failed to connect to AWS. Check credentials.", "error")
            except Exception as e:
                log_and_display(self.instance_info_text, f"An error occurred while setting up AWS session: {str(e)}", "error")
        else:
            log_and_display(self.instance_info_text, "Invalid AWS credentials provided.", "warning")

    def show_instance_management_screen(self):
        # Clear the current screen
        for widget in self.winfo_children():
            widget.destroy()

        # Add instance management widgets
        self.instance_list_label = ctk.CTkLabel(self, text="Instances:")
        self.instance_list_label.pack(pady=5)

        self.instance_listbox = tk.Listbox(self)
        self.instance_listbox.pack(pady=5, fill='both', expand=True)
        self.instance_listbox.bind('<<ListboxSelect>>', self.on_instance_select)

        self.refresh_button = ctk.CTkButton(self, text="Refresh Instances", command=self.update_instance_list)
        self.refresh_button.pack(pady=5)

        self.start_button = ctk.CTkButton(self, text="Start Instance", command=self.start_instance)
        self.start_button.pack(pady=5)

        self.stop_button = ctk.CTkButton(self, text="Stop Instance", command=self.stop_instance)
        self.stop_button.pack(pady=5)

        self.reboot_button = ctk.CTkButton(self, text="Reboot Instance", command=self.reboot_instance)
        self.reboot_button.pack(pady=5)

        self.instance_info_text = ctk.CTkTextbox(self, width=400, height=200)
        self.instance_info_text.pack(pady=10)

        # Populate the instance list
        self.update_instance_list()

    def update_instance_list(self):
        if self.aws_session:
            instances = list_instances(self.aws_session)
            if instances:
                self.instance_listbox.delete(0, 'end')
                for instance in instances:
                    instance_id = instance['InstanceId']
                    nickname = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'No Nickname')
                    display_text = f"{instance_id} ({nickname})"
                    self.instance_listbox.insert('end', display_text)
                log_and_display(self.instance_info_text, "Instances retrieved successfully.")
            else:
                log_and_display(self.instance_info_text, "No instances found.", "warning")

    def on_instance_select(self, event):
        selected_instance = self.instance_listbox.get(self.instance_listbox.curselection())
        instance_id = selected_instance.split(' ')[0]
        self.show_instance_info(instance_id)

    def show_instance_info(self, instance_id):
        instance_info = get_instance_network_info(self.aws_session, instance_id)
        if instance_info:
            formatted_info = format_instance_info(instance_info)
            log_and_display(self.instance_info_text, formatted_info)
        else:
            log_and_display(self.instance_info_text, f"Failed to retrieve info for instance {instance_id}.", "error")

    def start_instance(self):
        selected_instance = self.instance_listbox.get(self.instance_listbox.curselection())
        instance_id = selected_instance.split(' ')[0]
        if start_instance(self.aws_session, instance_id):
            log_and_display(self.instance_info_text, f"Instance {instance_id} started successfully.")
        else:
            log_and_display(self.instance_info_text, f"Failed to start instance {instance_id}.", "error")

    def stop_instance(self):
        selected_instance = self.instance_listbox.get(self.instance_listbox.curselection())
        instance_id = selected_instance.split(' ')[0]
        if stop_instance(self.aws_session, instance_id):
            log_and_display(self.instance_info_text, f"Instance {instance_id} stopped successfully.")
        else:
            log_and_display(self.instance_info_text, f"Failed to stop instance {instance_id}.", "error")

    def reboot_instance(self):
        selected_instance = self.instance_listbox.get(self.instance_listbox.curselection())
        instance_id = selected_instance.split(' ')[0]
        if reboot_instance(self.aws_session, instance_id):
            log_and_display(self.instance_info_text, f"Instance {instance_id} rebooted successfully.")
        else:
            log_and_display(self.instance_info_text, f"Failed to reboot instance {instance_id}.", "error")
