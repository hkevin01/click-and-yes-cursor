#!/usr/bin/env python3
"""
Smart Linux automation - excludes automation window, targets real Cursor editors
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

def run_command(cmd, timeout=10):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", f"Command timed out after {timeout}s", 1
    except Exception as e:
        return "", str(e), 1

def get_current_window_info():
    try:
        current_id, _, _ = run_command('xdotool getwindowfocus')
        current_name, _, _ = run_command('xdotool getwindowfocus getwindowname')
        return current_id.strip(), current_name.strip()
    except Exception:
        return None, None

def get_config():
    try:
        config_path = os.path.join(os.path.dirname(__file__), '../src/config.json')
        with open(config_path, encoding='utf-8') as f:
            config = json.load(f)
        windows = config.get('windows', [])
        messages = config.get('message', ["yes, continue"])
        processed_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                processed_messages.append(msg.get('text', str(msg)))
            else:
                processed_messages.append(str(msg))
        cycling = config.get('cycling', 'round_robin')
        window_cycling = config.get('window_cycling', 'round_robin')
        fallback_to_coordinates = config.get('fallback_to_coordinates', True)
        return windows, processed_messages, cycling, window_cycling, fallback_to_coordinates
    except Exception as e:
        log_with_time(f"Config error: {e}")
        default_window = {
            'title': 'Cursor',
            'coordinates': {'x': 500, 'y': 300},
            'enabled': True
        }
        return [default_window], ["test message"], 'round_robin', 'round_robin', True

def should_exclude_window(window_title, window_id, current_window_id, current_window_name, exclude_patterns):
    # Exclude current window
    if window_id == current_window_id:
        log_with_time(f"Excluding current window: {window_title}")
        return True
    if "click-and-yes-cursor" in window_title.lower():
        log_with_time(f"Excluding automation project window: {window_title}")
        return True
    if "terminal" in window_title.lower() and ("run.sh" in window_title.lower() or "automation" in window_title.lower()):
        log_with_time(f"Excluding terminal running automation: {window_title}")
        return True
    if "visual studio code" in window_title.lower() and "click-and-yes-cursor" in window_title.lower():
        log_with_time(f"Excluding VS Code automation window: {window_title}")
        return True
    for pattern in exclude_patterns:
        if pattern.lower() in window_title.lower():
            log_with_time(f"Excluding window matching pattern '{pattern}': {window_title}")
            return True
    return False

def find_target_windows(target_title, current_window_id, current_window_name, exclude_patterns):
    log_with_time(f"Searching for windows containing: '{target_title}'")
    stdout, stderr, returncode = run_command("wmctrl -l")
    if returncode != 0:
        log_with_time(f"wmctrl failed: {stderr}")
        return []
    candidates = []
    for line in stdout.split('\n'):
        if not line.strip():
            continue
        parts = line.split(None, 3)
        if len(parts) >= 4:
            window_id, desktop, host, window_title = parts[0], parts[1], parts[2], parts[3]
            if target_title.lower() in window_title.lower():
                if not should_exclude_window(window_title, window_id, current_window_id, current_window_name, exclude_patterns):
                    candidates.append((window_id, window_title))
                    log_with_time(f"Found valid target: {window_id} - {window_title}")
    log_with_time(f"Found {len(candidates)} valid target windows")
    return candidates

def get_next_window_index():
    index_file = os.path.join(os.path.dirname(__file__), '../logs/window_index.txt')
    try:
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                current_index = int(f.read().strip())
        else:
            current_index = 0
    except Exception:
        current_index = 0
    return current_index

def update_window_index(new_index):
    index_file = os.path.join(os.path.dirname(__file__), '../logs/window_index.txt')
    try:
        with open(index_file, 'w') as f:
            f.write(str(new_index))
    except Exception as e:
        log_with_time(f"Warning: Could not save window index: {e}")

def activate_window_by_id(window_id):
    log_with_time(f"Activating window ID: {window_id}")
    stdout, stderr, returncode = run_command(f"wmctrl -ia {window_id}")
    if returncode == 0:
        log_with_time("✓ Window activated successfully")
        time.sleep(0.5)
        return True
    else:
        log_with_time(f"Window activation failed: {stderr}")
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
        if isinstance(message, dict):
            message = message.get('text', str(message))
        message = str(message)
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

if __name__ == "__main__":
    log_with_time("=== SMART CURSOR AUTOMATION STARTING ===")
    try:
        current_window_id, current_window_name = get_current_window_info()
        log_with_time(f"Current window: {current_window_name} (ID: {current_window_id})")
        windows, messages, cycling, window_cycling, fallback_to_coordinates = get_config()
        if not windows:
            log_with_time("No windows configured")
            sys.exit(1)
        if not messages:
            log_with_time("No messages configured")
            sys.exit(1)
        all_target_windows = []
        for window_config in windows:
            if not window_config.get('enabled', True):
                continue
            title = window_config.get('title', '')
            exclude_patterns = window_config.get('exclude_if_contains', [])
            candidates = find_target_windows(title, current_window_id, current_window_name, exclude_patterns)
            for window_id, window_title in candidates:
                all_target_windows.append({
                    'id': window_id,
                    'title': window_title,
                    'coordinates': window_config.get('coordinates', {}),
                    'config': window_config
                })
        if not all_target_windows:
            log_with_time("No valid target windows found (all excluded or none match)")
            if windows and fallback_to_coordinates:
                log_with_time("Trying fallback coordinates from first window config")
                coords = windows[0].get('coordinates', {})
                if coords and 'x' in coords and 'y' in coords:
                    click_coordinates(coords['x'], coords['y'])
                    time.sleep(0.3)
                    send_message(messages[0])
            sys.exit(1)
        log_with_time(f"Found {len(all_target_windows)} valid target windows")
        for i, tw in enumerate(all_target_windows):
            log_with_time(f"  {i+1}. {tw['title']}")
        window_index = get_next_window_index()
        target_window = all_target_windows[window_index % len(all_target_windows)]
        update_window_index((window_index + 1) % len(all_target_windows))
        message_index = window_index % len(messages)
        message = messages[message_index]
        log_with_time(f"Target window {window_index + 1}/{len(all_target_windows)}: {target_window['title']}")
        log_with_time(f"Message: {str(message)[:50]}...")
        success = activate_window_by_id(target_window['id'])
        if success:
            success = send_message(message)
        else:
            log_with_time("Window activation failed, trying coordinates fallback")
            coords = target_window.get('coordinates', {})
            if coords and 'x' in coords and 'y' in coords:
                if click_coordinates(coords['x'], coords['y']):
                    time.sleep(0.3)
                    success = send_message(message)
        if success:
            log_with_time("✓ Automation completed successfully")
        else:
            log_with_time("⚠ Automation completed with issues")
        log_with_time("=== SMART CURSOR AUTOMATION COMPLETED ===")
    except Exception as e:
        log_with_time(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
