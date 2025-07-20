#!/usr/bin/env python3
"""
Enhanced Linux automation script - no hanging, better error handling
"""
import datetime
import json
import os
import subprocess
import sys
import time
import random

def log_with_time(msg):
    now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{now} {msg}")
    sys.stdout.flush()

def run_command(cmd, timeout=10):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", f"Command timed out after {timeout}s", 1
    except Exception as e:
        return "", str(e), 1

def get_config():
    try:
        config_path = os.path.join(os.path.dirname(__file__), '../src/config.json')
        with open(config_path, encoding='utf-8') as f:
            config = json.load(f)
        # Convert old format if needed
        if 'coordinates' in config and 'windows' not in config:
            coords = config.get('coordinates', {'x': 100, 'y': 200})
            config['windows'] = [{
                'title': 'Default Window',
                'coordinates': coords,
                'enabled': True
            }]
        windows = config.get('windows', [])
        messages = config.get('message', ["yes, continue"])
        cycling = config.get('cycling', 'round_robin')
        window_cycling = config.get('window_cycling', 'round_robin')
        fallback_to_coordinates = config.get('fallback_to_coordinates', True)
        return windows, messages, cycling, window_cycling, fallback_to_coordinates
    except Exception as e:
        log_with_time(f"Config error: {e}")
        # Return safe defaults
        default_window = {
            'title': 'Default',
            'coordinates': {'x': 100, 'y': 200},
            'enabled': True
        }
        return [default_window], ["test message"], 'round_robin', 'round_robin', True

def find_window_by_title(title):
    log_with_time(f"Searching for window: {title}")
    stdout, stderr, returncode = run_command("wmctrl -l")
    if returncode != 0:
        log_with_time(f"wmctrl failed: {stderr}")
        return None
    for line in stdout.split('\n'):
        if not line.strip():
            continue
        parts = line.split(None, 3)
        if len(parts) >= 4:
            window_id, desktop, host, window_title = parts[0], parts[1], parts[2], parts[3]
            if title.lower() in window_title.lower():
                log_with_time(f"Found window: {window_id} - {window_title}")
                return window_id
    log_with_time(f"Window not found: {title}")
    return None

def activate_window(window_id):
    log_with_time(f"Activating window: {window_id}")
    stdout, stderr, returncode = run_command(f"wmctrl -ia {window_id}")
    if returncode == 0:
        log_with_time("✓ Window activated")
        time.sleep(0.3)
        return True
    else:
        log_with_time(f"Window activation failed: {stderr}")
        return False

def activate_window_xdotool(title):
    log_with_time(f"Trying xdotool activation for: {title}")
    stdout, stderr, returncode = run_command(f'xdotool search --name "{title}" | head -1')
    if returncode != 0 or not stdout:
        log_with_time(f"xdotool search failed: {stderr}")
        return False
    window_id = stdout.strip()
    log_with_time(f"Found window ID: {window_id}")
    stdout, stderr, returncode = run_command(f'xdotool windowactivate {window_id}')
    if returncode == 0:
        log_with_time("✓ Window activated with xdotool")
        time.sleep(0.3)
        return True
    else:
        log_with_time(f"xdotool activation failed: {stderr}")
        return False

def click_coordinates(x, y):
    log_with_time(f"Clicking at coordinates: ({x}, {y})")
    stdout, stderr, returncode = run_command(f'xdotool mousemove {x} {y}')
    if returncode != 0:
        log_with_time(f"Mouse move failed: {stderr}")
        return False
    time.sleep(0.1)
    stdout, stderr, returncode = run_command('xdotool click 1')
    if returncode != 0:
        log_with_time(f"Click failed: {stderr}")
        return False
    log_with_time("✓ Click successful")
    return True

def send_message(message):
    try:
        import pyperclip
        now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        full_message = f"{now} {message}"
        log_with_time(f"Sending message: {message[:50]}...")
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
    except Exception as e:
        log_with_time(f"Send message failed: {e}")
        return False

def process_window(window, message, fallback_to_coordinates=True):
    title = window.get('title', '')
    coordinates = window.get('coordinates', {})
    log_with_time(f"Processing window: {title}")
    window_activated = False
    if title:
        window_id = find_window_by_title(title)
        if window_id:
            window_activated = activate_window(window_id)
        if not window_activated:
            window_activated = activate_window_xdotool(title)
    if coordinates and ('x' in coordinates and 'y' in coordinates):
        if not window_activated and fallback_to_coordinates:
            log_with_time("Using fallback coordinates")
            x, y = coordinates['x'], coordinates['y']
            if click_coordinates(x, y):
                time.sleep(0.3)
    # Ensure message is a string before slicing
    if not isinstance(message, str):
        message_str = str(message)
    else:
        message_str = message
    log_with_time(f"Message: {message_str[:50]}...")
    log_with_time(f"Fallback to coordinates: {fallback_to_coordinates}")
    return send_message(message)

if __name__ == "__main__":
    log_with_time("=== ENHANCED LINUX AUTOMATION STARTING ===")
    try:
        windows, messages, cycling, window_cycling, fallback_to_coordinates = get_config()
        if not windows:
            log_with_time("No windows configured")
            sys.exit(1)
        if not messages:
            log_with_time("No messages configured")
            sys.exit(1)
        enabled_windows = [w for w in windows if w.get('enabled', True)]
        if not enabled_windows:
            log_with_time("No enabled windows found")
            sys.exit(1)
        target_window = enabled_windows[0]
        message = messages[0]
        log_with_time(f"Target window: {target_window.get('title', 'Unknown')}")
        # Ensure message is a string before slicing
        if not isinstance(message, str):
            message_str = str(message)
        else:
            message_str = message
        log_with_time(f"Message: {message_str[:50]}...")
        log_with_time(f"Fallback to coordinates: {fallback_to_coordinates}")
        success = process_window(target_window, message, fallback_to_coordinates)
        if success:
            log_with_time("✓ Automation completed successfully")
        else:
            log_with_time("⚠ Automation completed with some issues")
        log_with_time("=== ENHANCED LINUX AUTOMATION COMPLETED ===")
    except Exception as e:
        log_with_time(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
