#!/usr/bin/env python3
"""
Non-hanging version of the automation script
"""
import datetime
import json
import os
import subprocess
import sys
import time

def log_with_time(msg):
    now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{now} {msg}")
    sys.stdout.flush()

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def get_config():
    try:
        with open(os.path.join(os.path.dirname(__file__), '../src/config.json'), encoding='utf-8') as f:
            config = json.load(f)
        if 'coordinates' in config and 'windows' not in config:
            coords = config.get('coordinates', {'x': 100, 'y': 200})
            config['windows'] = [{
                'title': 'Default Window',
                'coordinates': coords,
                'enabled': True
            }]
        windows = config.get('windows', [])
        messages = config.get('message', ["yes, continue"])
        return windows, messages
    except Exception as e:
        log_with_time(f"Config error: {e}")
        return [], ["test message"]

def activate_window_xdotool(title):
    """Use xdotool instead of wmctrl to avoid potential hangs"""
    log_with_time(f"Activating window with xdotool: {title}")
    cmd = f'xdotool search --name "{title}" | head -1'
    stdout, stderr, returncode = run_command(cmd)
    if returncode == 0 and stdout:
        window_id = stdout.strip()
        log_with_time(f"Found window ID: {window_id}")
        cmd = f'xdotool windowactivate {window_id}'
        stdout, stderr, returncode = run_command(cmd)
        if returncode == 0:
            log_with_time("✓ Window activated successfully")
            return True
        else:
            log_with_time(f"Failed to activate: {stderr}")
    return False

def send_message_xdotool(message):
    """Send message using xdotool instead of pyautogui"""
    log_with_time(f"Sending message: {message[:30]}...")
    import pyperclip
    now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_message = f"{now} {message}"
    pyperclip.copy(full_message)
    time.sleep(0.2)
    stdout, stderr, returncode = run_command('xdotool key ctrl+v')
    if returncode != 0:
        log_with_time(f"Paste failed: {stderr}")
        return False
    time.sleep(0.2)
    stdout, stderr, returncode = run_command('xdotool key Return')
    if returncode != 0:
        log_with_time(f"Enter failed: {stderr}")
        return False
    log_with_time("✓ Message sent successfully")
    return True

if __name__ == "__main__":
    log_with_time("=== NON-HANGING AUTOMATION STARTING ===")
    try:
        windows, messages = get_config()
        if not windows:
            log_with_time("No windows configured")
            sys.exit(1)
        target_window = next((w for w in windows if w.get('enabled', True)), None)
        if not target_window:
            log_with_time("No enabled windows")
            sys.exit(1)
        message = messages[0] if messages else "test message"
        log_with_time(f"Target: {target_window.get('title', 'Unknown')}")
        log_with_time(f"Message: {message[:30]}...")
        if activate_window_xdotool(target_window.get('title', '')):
            send_message_xdotool(message)
        else:
            log_with_time("Window activation failed, but script completed")
        log_with_time("=== NON-HANGING AUTOMATION COMPLETED ===")
    except Exception as e:
        log_with_time(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
