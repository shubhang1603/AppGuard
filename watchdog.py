import psutil
import time
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FLAGS_FILE = os.path.join(SCRIPT_DIR, 'auth_flags.json')


# Map process names to human-friendly names
PROTECTED_APPS = {
    "WhatsApp.exe": "WhatsApp",
}

# Give new processes a few seconds before checking flag
GRACE_PERIOD_SECONDS = 1
tracked_processes = {}

def is_app_allowed(app_label):
    if not os.path.exists(FLAGS_FILE):
        return False
    try:
        with open(FLAGS_FILE, 'r') as f:
            flags = json.load(f)
        return flags.get(app_label, False)
    except json.JSONDecodeError:
        return False

def kill_process(proc):
    try:
        proc.kill()
        print(f"[AppGuard] Killed: {proc.name()}")
    except Exception as e:
        print(f"[AppGuard] Failed to kill {proc.name()}: {e}")

def main():
    print("[AppGuard] Watchdog running...")
    while True:
        current_time = time.time()
        for proc in psutil.process_iter(['pid', 'name', 'create_time']):
            pname = proc.info['name']
            if pname in PROTECTED_APPS:
                pid = proc.info['pid']
                app_label = PROTECTED_APPS[pname]
                allowed = is_app_allowed(app_label)

                # Track when we first saw the process
                if pid not in tracked_processes:
                    tracked_processes[pid] = proc.info['create_time']

                # Check if grace period has passed
                start_time = tracked_processes[pid]
                if (current_time - start_time) >= GRACE_PERIOD_SECONDS:
                    if not allowed:
                        kill_process(proc)
                        # Remove from tracking so it doesn’t get checked again
                        tracked_processes.pop(pid, None)

        # Clean up dead processes from tracking
        active_pids = {p.info['pid'] for p in psutil.process_iter(['pid'])}
        tracked_processes_keys = list(tracked_processes.keys())
        for pid in tracked_processes_keys:
            if pid not in active_pids:
                tracked_processes.pop(pid, None)

        time.sleep(1)

if __name__ == "__main__":
    main()
