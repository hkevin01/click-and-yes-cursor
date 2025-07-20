#!/usr/bin/env python3
"""
Debug version to identify where the script hangs
"""
import sys
import os
import json
import subprocess
import time

def log_debug(msg):
    print(f"[DEBUG] {msg}")
    sys.stdout.flush()

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1

if __name__ == "__main__":
    log_debug("Script starting...")
    try:
        log_debug("Testing basic imports...")
        import datetime
        import logging
        import platform
        import random
        log_debug("✓ Basic imports successful")
        log_debug("Testing pyautogui import...")
        import pyautogui
        log_debug("✓ pyautogui imported")
        log_debug("Testing pyperclip import...")
        import pyperclip
        log_debug("✓ pyperclip imported")
        log_debug("Testing config file read...")
        config_path = os.path.join(os.path.dirname(__file__), '../src/config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        log_debug(f"✓ Config loaded: {len(config)} keys")
        log_debug("Testing wmctrl command...")
        stdout, stderr, returncode = run_command("wmctrl -l")
        if returncode == 0:
            lines = stdout.split('\n')
            log_debug(f"✓ wmctrl found {len(lines)} windows")
        else:
            log_debug(f"✗ wmctrl failed: {stderr}")
        log_debug("Testing pyautogui.FAILSAFE...")
        pyautogui.FAILSAFE = False
        log_debug("✓ pyautogui.FAILSAFE set")
        log_debug("Testing pyperclip...")
        pyperclip.copy("test")
        content = pyperclip.paste()
        log_debug(f"✓ pyperclip test: {content}")
        log_debug("All tests completed successfully!")
    except Exception as e:
        log_debug(f"✗ Error at: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
