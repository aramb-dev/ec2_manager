# gui/main_window.py

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
from aws_connection import setup_aws_session, list_instances, start_instance, stop_instance, reboot_instance, get_instance_network_info
from utils import log_and_display, validate_aws_credentials, format_instance_info

class EC2ManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EC2 Manager")
        self.geometry("600x400")
        self.aws_session = None
        self.instance_cache = None  # Cache for instance list
        self.credentials = None  # Store credentials for reconnect

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
            # Store credentials for reconnect (only region, not keys)
            self.credentials = {'region': region}

            # Connect in background thread
            def connect():
                self.after(0, lambda: self.connect_button.configure(state="disabled", text="Connecting..."))
                self.after(0, lambda: log_and_display(self.instance_info_text, "Connecting to AWS..."))

                try:
                    session = setup_aws_session(aws_access_key, aws_secret_key, region)
                    if session:
                        self.aws_session = session
                        self.after(0, lambda: log_and_display(self.instance_info_text, "Connected to AWS successfully!"))
                        self.after(0, self.show_instance_management_screen)
                    else:
                        self.after(0, lambda: log_and_display(
                            self.instance_info_text,
                            "Failed to connect to AWS. Check credentials.",
                            "error"
                        ))
                        self.after(0, lambda: self.connect_button.configure(state="normal", text="Connect to AWS"))
                except Exception as e:
                    self.after(0, lambda: log_and_display(
                        self.instance_info_text,
                        f"An error occurred while setting up AWS session: {str(e)}",
                        "error"
                    ))
                    self.after(0, lambda: self.connect_button.configure(state="normal", text="Connect to AWS"))

            thread = threading.Thread(target=connect, daemon=True)
            thread.start()
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

        self.refresh_button = ctk.CTkButton(self, text="Refresh Instances", command=lambda: self.update_instance_list(use_cache=False))
        self.refresh_button.pack(pady=5)

        self.start_button = ctk.CTkButton(self, text="Start Instance", command=self.start_instance)
        self.start_button.pack(pady=5)

        self.stop_button = ctk.CTkButton(self, text="Stop Instance", command=self.stop_instance)
        self.stop_button.pack(pady=5)

        self.reboot_button = ctk.CTkButton(self, text="Reboot Instance", command=self.reboot_instance)
        self.reboot_button.pack(pady=5)

        self.instance_info_text = ctk.CTkTextbox(self, width=400, height=200)
        self.instance_info_text.pack(pady=10)

        # Disconnect button
        self.disconnect_button = ctk.CTkButton(self, text="Disconnect", command=self.disconnect_aws)
        self.disconnect_button.pack(pady=5)

        # Bind keyboard shortcuts
        self.bind('<Control-r>', lambda e: self.update_instance_list(use_cache=False))
        self.bind('<Control-s>', lambda e: self.start_instance())
        self.bind('<Control-t>', lambda e: self.stop_instance())
        self.bind('<Control-b>', lambda e: self.reboot_instance())
        self.bind('<F5>', lambda e: self.update_instance_list(use_cache=False))
        self.bind('<Control-d>', lambda e: self.disconnect_aws())

        # Populate the instance list
        self.update_instance_list()

    def _set_buttons_state(self, state):
        """Helper method to enable/disable action buttons."""
        self.refresh_button.configure(state=state)
        self.start_button.configure(state=state)
        self.stop_button.configure(state=state)
        self.reboot_button.configure(state=state)
        self.disconnect_button.configure(state=state)

    def _get_selected_instance_id(self):
        """Helper method to get the selected instance ID from listbox."""
        selection = self.instance_listbox.curselection()
        if not selection:
            return None
        selected_instance = self.instance_listbox.get(selection)
        return selected_instance.split(' ')[0]

    def _perform_instance_action(self, action_func, action_name, confirm=False):
        """
        Generic method to perform instance actions (start, stop, reboot).

        Args:
            action_func: The function to call (start_instance, stop_instance, reboot_instance)
            action_name: Display name of the action (e.g., "start", "stop", "reboot")
            confirm: Whether to show confirmation dialog before action
        """
        instance_id = self._get_selected_instance_id()
        if not instance_id:
            log_and_display(self.instance_info_text, "Please select an instance first.", "warning")
            return

        # Confirmation dialog for destructive operations
        if confirm:
            if not messagebox.askyesno(
                f"Confirm {action_name.capitalize()}",
                f"Are you sure you want to {action_name} instance {instance_id}?"
            ):
                return

        # Perform action in background thread
        def run_action():
            self.after(0, lambda: self._set_buttons_state("disabled"))
            self.after(0, lambda: log_and_display(
                self.instance_info_text,
                f"{action_name.capitalize()}ing instance {instance_id}..."
            ))

            success = action_func(self.aws_session, instance_id)

            if success:
                self.after(0, lambda: log_and_display(
                    self.instance_info_text,
                    f"✓ Instance {instance_id} {action_name}ed successfully."
                ))
                # Invalidate cache after state change
                self.instance_cache = None
            else:
                self.after(0, lambda: log_and_display(
                    self.instance_info_text,
                    f"✗ Failed to {action_name} instance {instance_id}.",
                    "error"
                ))

            self.after(0, lambda: self._set_buttons_state("normal"))

        thread = threading.Thread(target=run_action, daemon=True)
        thread.start()

    def disconnect_aws(self):
        """Disconnect from AWS and return to login screen."""
        self.aws_session = None
        self.instance_cache = None

        # Clear the screen
        for widget in self.winfo_children():
            widget.destroy()

        # Recreate login screen
        self.access_key_label = ctk.CTkLabel(self, text="AWS Access Key:")
        self.access_key_label.pack(pady=5)
        self.access_key_entry = ctk.CTkEntry(self, show="*")
        self.access_key_entry.pack(pady=5)

        self.secret_key_label = ctk.CTkLabel(self, text="AWS Secret Key:")
        self.secret_key_label.pack(pady=5)
        self.secret_key_entry = ctk.CTkEntry(self, show="*")
        self.secret_key_entry.pack(pady=5)

        self.region_label = ctk.CTkLabel(self, text="AWS Region:")
        self.region_label.pack(pady=5)
        self.region_entry = ctk.CTkEntry(self)
        self.region_entry.pack(pady=5)

        # Pre-fill credentials if available
        if self.credentials:
            self.access_key_entry.insert(0, "***")
            self.secret_key_entry.insert(0, "***")
            self.region_entry.insert(0, self.credentials.get('region', ''))

        self.connect_button = ctk.CTkButton(self, text="Connect to AWS", command=self.connect_aws)
        self.connect_button.pack(pady=10)

        self.instance_info_text = ctk.CTkTextbox(self, width=400, height=200)
        self.instance_info_text.pack(pady=10)

        log_and_display(self.instance_info_text, "Disconnected from AWS.")

    def update_instance_list(self, use_cache=True):
        """
        Update the instance list, optionally using cached data.

        Args:
            use_cache: If True and cache exists, use cached data. If False, force refresh.
        """
        if not self.aws_session:
            return

        # Use cache if available and requested
        if use_cache and self.instance_cache is not None:
            self._display_instances(self.instance_cache)
            log_and_display(self.instance_info_text, f"✓ Loaded {len(self.instance_cache)} instance(s) from cache.")
            return

        # Fetch from AWS in background thread
        def fetch_instances():
            self.after(0, lambda: self._set_buttons_state("disabled"))
            self.after(0, lambda: log_and_display(self.instance_info_text, "Loading instances..."))

            instances = list_instances(self.aws_session)

            if instances is None:
                self.after(0, lambda: log_and_display(
                    self.instance_info_text,
                    "Failed to retrieve instances. Check your AWS permissions.",
                    "error"
                ))
            elif instances:
                self.instance_cache = instances  # Cache the results
                self.after(0, lambda: self._display_instances(instances))
                self.after(0, lambda: log_and_display(
                    self.instance_info_text,
                    f"✓ Loaded {len(instances)} instance(s) successfully."
                ))
            else:
                self.instance_cache = []
                self.after(0, lambda: log_and_display(
                    self.instance_info_text,
                    "No instances found.",
                    "warning"
                ))

            self.after(0, lambda: self._set_buttons_state("normal"))

        thread = threading.Thread(target=fetch_instances, daemon=True)
        thread.start()

    def _display_instances(self, instances):
        """Helper method to display instances in the listbox."""
        self.instance_listbox.delete(0, 'end')
        for instance in instances:
            instance_id = instance['InstanceId']
            nickname = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'No Nickname')
            display_text = f"{instance_id} ({nickname})"
            self.instance_listbox.insert('end', display_text)

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
        """Start the selected EC2 instance."""
        self._perform_instance_action(start_instance, "start", confirm=False)

    def stop_instance(self):
        """Stop the selected EC2 instance."""
        self._perform_instance_action(stop_instance, "stop", confirm=True)

    def reboot_instance(self):
        """Reboot the selected EC2 instance."""
        self._perform_instance_action(reboot_instance, "reboot", confirm=True)
