#!/usr/bin/env python3
"""
Minimal test without pyautogui to isolate the hanging issue
"""
import datetime
import json
import os
import subprocess
import sys

def log_with_time(msg):
    now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{now} {msg}")
    sys.stdout.flush()

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

if __name__ == "__main__":
    log_with_time("=== MINIMAL TEST STARTING ===")
    try:
        log_with_time("1. Testing basic imports...")
        import time
        import random
        log_with_time("✓ Basic imports OK")
        log_with_time("2. Testing config file...")
        config_path = os.path.join(os.path.dirname(__file__), '../src/config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        log_with_time(f"✓ Config loaded: {len(config)} keys")
        log_with_time("3. Testing wmctrl...")
        stdout, stderr, returncode = run_command("wmctrl -l")
        if returncode == 0:
            lines = stdout.split('\n')
            log_with_time(f"✓ wmctrl found {len(lines)} windows")
        else:
            log_with_time(f"✗ wmctrl failed: {stderr}")
        log_with_time("4. Testing pyperclip...")
        import pyperclip
        pyperclip.copy("test")
        content = pyperclip.paste()
        log_with_time(f"✓ pyperclip works: '{content}'")
        log_with_time("=== MINIMAL TEST COMPLETED SUCCESSFULLY ===")
    except Exception as e:
        log_with_time(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
