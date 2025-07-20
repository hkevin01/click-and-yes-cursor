#!/usr/bin/env python3
"""
Debug version of the Linux automation script
"""
import datetime
import json
import logging
import os
import platform
import random
import subprocess
import sys
import time

def log_debug(msg):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} [DEBUG] {msg}")
    sys.stdout.flush()

def run_command(cmd):
    log_debug(f"Running command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        log_debug(f"Command completed with exit code: {result.returncode}")
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        log_debug("Command timed out")
        return "", "Command timed out", 1
    except Exception as e:
        log_debug(f"Command failed with exception: {e}")
        return "", str(e), 1

def check_environment():
    log_debug("Checking environment...")
    log_debug(f"Platform: {platform.system()}")
    log_debug(f"DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")
    log_debug(f"XDG_SESSION_TYPE: {os.environ.get('XDG_SESSION_TYPE', 'Not set')}")

def test_imports():
    log_debug("Testing imports...")
    try:
        import pyautogui
        log_debug("✓ pyautogui imported")
        import pyperclip
        log_debug("✓ pyperclip imported")
        return True
    except Exception as e:
        log_debug(f"✗ Import failed: {e}")
        return False

def get_config():
    log_debug("Loading configuration...")
    try:
        config_path = os.path.join(os.path.dirname(__file__), '../src/config.json')
        log_debug(f"Config path: {config_path}")
        with open(config_path, encoding='utf-8') as f:
            config = json.load(f)
        log_debug(f"Config loaded with {len(config)} keys")
        # Convert old format if needed
        if 'coordinates' in config and 'windows' not in config:
            log_debug("Converting old config format...")
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
        log_debug(f"Found {len(windows)} windows, {len(messages)} messages")
        return windows, messages, cycling, window_cycling, fallback_to_coordinates
    except Exception as e:
        log_debug(f"Config loading failed: {e}")
        default_window = {'title': 'Default', 'coordinates': {'x': 100, 'y': 200}, 'enabled': True}
        return [default_window], ["yes, continue"], 'round_robin', 'round_robin', True

def list_windows():
    log_debug("Listing available windows...")
    stdout, stderr, returncode = run_command("wmctrl -l")
    if returncode == 0:
        lines = [line for line in stdout.split('\n') if line.strip()]
        log_debug(f"Found {len(lines)} windows")
        for i, line in enumerate(lines[:3]):  # Show first 3
            parts = line.split(None, 3)
            if len(parts) >= 4:
                log_debug(f"  {i+1}. {parts[0]} - {parts[3]}")
        return True
    else:
        log_debug(f"Failed to list windows: {stderr}")
        return False

if __name__ == "__main__":
    log_debug("=== DEBUG AUTOMATION SCRIPT STARTING ===")
    try:
        check_environment()
        if not test_imports():
            sys.exit(1)
        log_debug("Setting up pyautogui...")
        import pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.1
        log_debug("✓ pyautogui configured")
        windows, messages, cycling, window_cycling, fallback = get_config()
        if not list_windows():
            log_debug("Window listing failed, but continuing...")
        log_debug("Testing clipboard...")
        import pyperclip
        test_message = "test message from debug script"
        pyperclip.copy(test_message)
        clipboard_content = pyperclip.paste()
        if clipboard_content == test_message:
            log_debug("✓ Clipboard test successful")
        else:
            log_debug(f"✗ Clipboard test failed: got '{clipboard_content}'")
        log_debug("=== DEBUG SCRIPT COMPLETED SUCCESSFULLY ===")
    except Exception as e:
        log_debug(f"=== DEBUG SCRIPT FAILED: {e} ===")
        import traceback
        traceback.print_exc()
        sys.exit(1)
