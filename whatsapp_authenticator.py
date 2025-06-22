import hashlib
import subprocess
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import time
import psutil

print("[DEBUG] Working directory:", os.getcwd())



SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FLAGS_FILE = os.path.join(SCRIPT_DIR, 'auth_flags.json')
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'whatsapp_auth_config.txt')

print(f"[DEBUG] Reading flags from: {FLAGS_FILE}")


APP_NAME = "WhatsApp"
APP_PROCESS_NAME = "WhatsApp.exe"

class WhatsAppAuthenticator:
    def __init__(self):
        self.password_hash = None
        self.load_password()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def save_password(self, password):
        self.password_hash = self.hash_password(password)
        with open(CONFIG_FILE, 'w') as f:
            f.write(self.password_hash)

    def load_password(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                self.password_hash = f.read().strip()

    def verify_password(self, password):
        return self.hash_password(password) == self.password_hash

    def setup_password_gui(self):
        root = tk.Tk()
        root.withdraw()
        password = simpledialog.askstring("Setup Password", "Set master password:", show='*')
        if not password:
            return False
        confirm = simpledialog.askstring("Confirm Password", "Confirm password:", show='*')
        if password == confirm:
            self.save_password(password)
            messagebox.showinfo("Success", "Password set.")
            return True
        else:
            messagebox.showerror("Error", "Passwords do not match.")
            return self.setup_password_gui()

    def authenticate_gui(self):
        root = tk.Tk()
        root.withdraw()

        if not self.password_hash:
            messagebox.showinfo("Setup", "No password found. Set a new password.")
            return self.setup_password_gui()

        for attempt in range(3, 0, -1):
            password = simpledialog.askstring("Authentication", f"Enter password ({attempt} attempts left):", show='*')
            if password is None:
                return False
            if self.verify_password(password):
                return True
            else:
                messagebox.showerror("Wrong Password", "Incorrect password.")
        return False

def set_app_permission(app_name, allowed):
    flags = {}
    if os.path.exists(FLAGS_FILE):
        try:
            with open(FLAGS_FILE, 'r') as f:
                flags = json.load(f)
        except json.JSONDecodeError:
            flags = {}
    flags[app_name] = allowed
    if allowed:
        flags[f"{app_name}_timestamp"] = time.time()
    else:
        flags.pop(f"{app_name}_timestamp", None)
    with open(FLAGS_FILE, 'w') as f:
        json.dump(flags, f)

def launch_and_wait_for_process(process_name):
    try:
        # Launch WhatsApp UWP
        subprocess.Popen(['start', 'whatsapp:'], shell=True)

        # Wait for the actual process to appear
        print("Waiting for WhatsApp process to show up...")
        for _ in range(10):  # max 10 seconds
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == process_name:
                    print("WhatsApp process detected.")
                    return True
            time.sleep(1)
        print("WhatsApp did not launch within expected time.")
        return False
    except Exception as e:
        messagebox.showerror("Launch Failed", f"Could not launch WhatsApp: {e}")
        return False

def wait_for_app_close(process_name):
    while True:
        running = False
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == process_name:
                running = True
                break
        if not running:
            break
        time.sleep(1)


def main():
    auth = WhatsAppAuthenticator()
    if auth.authenticate_gui():
        set_app_permission(APP_NAME, True)
        launched = launch_and_wait_for_process(APP_PROCESS_NAME)
        if launched:
            wait_for_app_close(APP_PROCESS_NAME)
            set_app_permission(APP_NAME, False)
        else:
            set_app_permission(APP_NAME, False)
    else:
        set_app_permission(APP_NAME, False)

if __name__ == "__main__":
    main()