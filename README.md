# AppGuard 🔒

**AppGuard** is a simple Python-based security utility that restricts access to selected desktop apps (like WhatsApp) using password authentication. Unauthorized attempts to open protected apps are detected and instantly blocked.

## ✨ Features

- Password-protected access to apps (e.g., WhatsApp)
- Background watchdog script that monitors and forcefully closes unauthorized launches
- Auto-launches on system startup
- Lightweight and runs silently in the background

## 🛠 How It Works

1. A watchdog script (`watchdog.py`) runs at system startup, monitoring processes like `WhatsApp.exe`.
2. The authenticator (`authenticator.py`) prompts for a password and sets a temporary flag if correct.
3. Once the user closes WhatsApp, the permission is revoked until re-authentication.
4. The watchdog reads this flag and blocks unauthorized launches.

## 📁 Project Structure

AppGuard/
├── authenticator.py
├── watchdog.py
├── auth_flags.json
├── whatsapp_auth_config.txt
├── watchdog.vbs
├── watchdog.bat
└── README.md


## 🚀 Setup Instructions

1. Clone the repo:  
   `git clone https://github.com/shubhang1603/AppGuard.git`

2. Install dependencies:  
   `pip install psutil`

3. Run `authenticator.py` to unlock WhatsApp

4. Add `watchdog.vbs` to the Windows Startup folder for automatic monitoring on boot.

## 🔒 Security Note

If the system is shut down before WhatsApp is closed, the permission flag may stay active. You can add a cleanup routine to reset `auth_flags.json` on boot (optional enhancement).

---

Feel free to contribute or raise issues!
