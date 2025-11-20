# gui/main_window.py

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
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
        self.access_key_entry = ctk.CTkEntry(self, show="*")
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
                # Show loading indicator
                self.connect_button.configure(state="disabled", text="Connecting...")
                log_and_display(self.instance_info_text, "Connecting to AWS...")
                self.update()  # Force UI update

                self.aws_session = setup_aws_session(aws_access_key, aws_secret_key, region)
                if self.aws_session:
                    log_and_display(self.instance_info_text, "Connected to AWS successfully!")
                    self.show_instance_management_screen()
                else:
                    log_and_display(self.instance_info_text, "Failed to connect to AWS. Check credentials.", "error")
                    self.connect_button.configure(state="normal", text="Connect to AWS")
            except Exception as e:
                log_and_display(self.instance_info_text, f"An error occurred while setting up AWS session: {str(e)}", "error")
                self.connect_button.configure(state="normal", text="Connect to AWS")
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

    def _set_buttons_state(self, state):
        """Helper method to enable/disable action buttons."""
        self.refresh_button.configure(state=state)
        self.start_button.configure(state=state)
        self.stop_button.configure(state=state)
        self.reboot_button.configure(state=state)

    def update_instance_list(self):
        if self.aws_session:
            # Show loading indicator
            self._set_buttons_state("disabled")
            log_and_display(self.instance_info_text, "Loading instances...")
            self.update()  # Force UI update

            instances = list_instances(self.aws_session)

            # Re-enable buttons
            self._set_buttons_state("normal")

            if instances is None:
                log_and_display(self.instance_info_text, "Failed to retrieve instances. Check your AWS permissions.", "error")
            elif instances:
                self.instance_listbox.delete(0, 'end')
                for instance in instances:
                    instance_id = instance['InstanceId']
                    nickname = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'No Nickname')
                    display_text = f"{instance_id} ({nickname})"
                    self.instance_listbox.insert('end', display_text)
                log_and_display(self.instance_info_text, f"✓ Loaded {len(instances)} instance(s) successfully.")
            else:
                log_and_display(self.instance_info_text, "No instances found.", "warning")

    def on_instance_select(self, event):
        selection = self.instance_listbox.curselection()
        if not selection:
            return
        selected_instance = self.instance_listbox.get(selection)
        instance_id = selected_instance.split(' ')[0]
        self.show_instance_info(instance_id)

    def show_instance_info(self, instance_id):
        # Show loading indicator
        log_and_display(self.instance_info_text, f"Loading details for {instance_id}...")
        self.update()

        instance_info = get_instance_network_info(self.aws_session, instance_id)
        if instance_info:
            formatted_info = format_instance_info(instance_info)
            log_and_display(self.instance_info_text, formatted_info)
        else:
            log_and_display(self.instance_info_text, f"✗ Failed to retrieve info for instance {instance_id}.", "error")

    def start_instance(self):
        selection = self.instance_listbox.curselection()
        if not selection:
            log_and_display(self.instance_info_text, "Please select an instance first.", "warning")
            return
        selected_instance = self.instance_listbox.get(selection)
        instance_id = selected_instance.split(' ')[0]

        # Show loading indicator
        self._set_buttons_state("disabled")
        log_and_display(self.instance_info_text, f"Starting instance {instance_id}...")
        self.update()

        if start_instance(self.aws_session, instance_id):
            log_and_display(self.instance_info_text, f"✓ Instance {instance_id} started successfully.")
        else:
            log_and_display(self.instance_info_text, f"✗ Failed to start instance {instance_id}.", "error")

        self._set_buttons_state("normal")

    def stop_instance(self):
        selection = self.instance_listbox.curselection()
        if not selection:
            log_and_display(self.instance_info_text, "Please select an instance first.", "warning")
            return
        selected_instance = self.instance_listbox.get(selection)
        instance_id = selected_instance.split(' ')[0]

        # Confirmation dialog for destructive operation
        if not messagebox.askyesno("Confirm Stop", f"Are you sure you want to stop instance {instance_id}?"):
            return

        # Show loading indicator
        self._set_buttons_state("disabled")
        log_and_display(self.instance_info_text, f"Stopping instance {instance_id}...")
        self.update()

        if stop_instance(self.aws_session, instance_id):
            log_and_display(self.instance_info_text, f"✓ Instance {instance_id} stopped successfully.")
        else:
            log_and_display(self.instance_info_text, f"✗ Failed to stop instance {instance_id}.", "error")

        self._set_buttons_state("normal")

    def reboot_instance(self):
        selection = self.instance_listbox.curselection()
        if not selection:
            log_and_display(self.instance_info_text, "Please select an instance first.", "warning")
            return
        selected_instance = self.instance_listbox.get(selection)
        instance_id = selected_instance.split(' ')[0]

        # Confirmation dialog for destructive operation
        if not messagebox.askyesno("Confirm Reboot", f"Are you sure you want to reboot instance {instance_id}?"):
            return

        # Show loading indicator
        self._set_buttons_state("disabled")
        log_and_display(self.instance_info_text, f"Rebooting instance {instance_id}...")
        self.update()

        if reboot_instance(self.aws_session, instance_id):
            log_and_display(self.instance_info_text, f"✓ Instance {instance_id} rebooted successfully.")
        else:
            log_and_display(self.instance_info_text, f"✗ Failed to reboot instance {instance_id}.", "error")

        self._set_buttons_state("normal")
