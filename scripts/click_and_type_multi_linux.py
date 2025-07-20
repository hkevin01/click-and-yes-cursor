#!/usr/bin/env python3
"""
Mouse-controlling automation that takes over mouse during operation
"""
import datetime
import json
import os
import signal
import subprocess
import sys
import time

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(signum, frame):
    global shutdown_requested
    shutdown_requested = True
    log_with_time(f"🛑 Shutdown requested (signal {signum}) at {datetime.datetime.now().strftime('%H:%M:%S')}")
    log_with_time("=== AUTOMATION TERMINATED BY USER ===")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

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

def get_current_mouse_position():
    try:
        stdout, _, _ = run_command('xdotool getmouselocation --shell')
        coords = {}
        for line in stdout.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                coords[key] = int(value)
        return coords.get('X', 0), coords.get('Y', 0)
    except:
        return 0, 0

def take_mouse_control(chat_x, chat_y):
    log_with_time("🎮 TAKING MOUSE CONTROL")
    original_x, original_y = get_current_mouse_position()
    log_with_time(f"Original mouse position: ({original_x}, {original_y})")
    for attempt in range(5):
        log_with_time(f"Force moving mouse to chat coordinates (attempt {attempt + 1}/5)")
        run_command(f'xdotool mousemove {chat_x} {chat_y}')
        time.sleep(0.1)
        current_x, current_y = get_current_mouse_position()
        if abs(current_x - chat_x) <= 5 and abs(current_y - chat_y) <= 5:
            log_with_time(f"✓ Mouse positioned at chat coordinates: ({current_x}, {current_y})")
            break
        else:
            log_with_time(f"⚠ Mouse drifted to ({current_x}, {current_y}), retrying...")
            time.sleep(0.05)
    return original_x, original_y

def restore_mouse_position(original_x, original_y):
    log_with_time(f"🎮 Restoring mouse to original position: ({original_x}, {original_y})")
    run_command(f'xdotool mousemove {original_x} {original_y}')
    log_with_time("✓ Mouse control released")

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
        return windows, processed_messages
    except Exception as e:
        log_with_time(f"Config error: {e}")
        default_window = {
            'title': 'Cursor',
            'coordinates': {'x': 1631, 'y': 1973},
            'enabled': True
        }
        return [default_window], ["test message"]

def should_exclude_window(window_title, window_id, current_window_id):
    if window_id == current_window_id:
        log_with_time(f"Excluding current window: {window_title}")
        return True
    if "click-and-yes-cursor" in window_title.lower():
        log_with_time(f"Excluding automation project window: {window_title}")
        return True
    return False

def find_target_windows(target_title, current_window_id, current_window_name):
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
    time.sleep(1.2)
    log_with_time(f"Clicking chat input at exact coordinates: ({chat_x}, {chat_y})")
    stdout, stderr, returncode = run_command(f'xdotool mousemove {chat_x} {chat_y}')
    if returncode != 0:
        log_with_time(f"Mouse move to chat failed: {stderr}")
        return False
    time.sleep(0.3)
    stdout, stderr, returncode = run_command('xdotool click 1')
    if returncode != 0:
        log_with_time(f"Click on chat failed: {stderr}")
        return False
    log_with_time("✓ Chat input area clicked and focused")
    time.sleep(0.8)
    return True

def send_message_to_chat(message):
    try:
        if isinstance(message, dict):
            message = message.get('text', str(message))
        message = str(message)
        now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        full_message = f"{now} {message}"
        log_with_time(f"Typing in chat: {message[:50]}...")
        stdout, stderr, returncode = run_command('xdotool key ctrl+a')
        time.sleep(0.2)
        escaped_message = full_message.replace('"', '\"').replace("'", "\\'").replace('`', '\`')
        stdout, stderr, returncode = run_command(f'xdotool type "{escaped_message}"')
        if returncode == 0:
            log_with_time("✓ Message typed into chat input")
            time.sleep(0.5)
            stdout, stderr, returncode = run_command('xdotool key Return')
            if returncode == 0:
                log_with_time("✓ Message sent to chat successfully")
                return True
            else:
                log_with_time(f"Enter key failed: {stderr}")
        else:
            log_with_time(f"Typing failed: {stderr}")
        return False
    except Exception as e:
        log_with_time(f"Send message failed: {e}")
        return False

if __name__ == "__main__":
    log_with_time("=== FIXED-COORDINATE CHAT AUTOMATION STARTING ===")
    try:
        current_window_id, current_window_name = get_current_window_info()
        log_with_time(f"Current window: {current_window_name} (ID: {current_window_id})")
        windows, messages = get_config()
        if not windows:
            log_with_time("No windows configured")
            sys.exit(1)
        if not messages:
            log_with_time("No messages configured")
            sys.exit(1)
        chat_coordinates = windows[0].get('coordinates', {})
        if not chat_coordinates or 'x' not in chat_coordinates or 'y' not in chat_coordinates:
            log_with_time("ERROR: No chat coordinates configured!")
            sys.exit(1)
        chat_x, chat_y = chat_coordinates['x'], chat_coordinates['y']
        log_with_time(f"Using fixed chat coordinates: ({chat_x}, {chat_y})")
        all_target_windows = []
        for window_config in windows:
            if not window_config.get('enabled', True):
                continue
            title = window_config.get('title', '')
            candidates = find_target_windows(title, current_window_id, current_window_name)
            for window_id, window_title in candidates:
                all_target_windows.append({
                    'id': window_id,
                    'title': window_title,
                    'chat_x': chat_x,
                    'chat_y': chat_y
                })
        if not all_target_windows:
            log_with_time("No valid target windows found")
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
        success = activate_window_and_focus_chat(
            target_window['id'],
            target_window['chat_x'],
            target_window['chat_y']
        )
        if success:
            success = send_message_to_chat(message)
        if success:
            log_with_time("✓ Fixed-coordinate chat automation completed successfully")
        else:
            log_with_time("⚠ Fixed-coordinate chat automation completed with issues")
        log_with_time("=== FIXED-COORDINATE CHAT AUTOMATION COMPLETED ===")
    except KeyboardInterrupt:
        log_with_time(f"🛑 Keyboard interrupt received at {datetime.datetime.now().strftime('%H:%M:%S')}")
        log_with_time("=== AUTOMATION TERMINATED BY USER ===")
        sys.exit(0)
    except Exception as e:
        log_with_time(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
