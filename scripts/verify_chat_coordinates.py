#!/usr/bin/env python3
"""
Tool to verify and adjust chat coordinates
"""
import subprocess
import time
import json
import os

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def main():
    print("=== CHAT COORDINATE VERIFICATION ===")
    print()
    config_path = os.path.join(os.path.dirname(__file__), '../src/config.json')
    with open(config_path) as f:
        config = json.load(f)
    coords = config['windows'][0]['coordinates']
    x, y = coords['x'], coords['y']
    print(f"Current configured coordinates: ({x}, {y})")
    print()
    print("This will test these coordinates by:")
    print("1. Moving mouse there")
    print("2. Clicking")
    print("3. Typing 'COORDINATE TEST MESSAGE'")
    print("4. Pressing Enter")
    print()
    stdout, _, _ = run_command("wmctrl -l | grep -i cursor")
    if not stdout:
        print("❌ No Cursor windows found!")
        return
    lines = stdout.split('\n')
    if lines:
        window_info = lines[0].split(None, 3)
        window_id = window_info[0]
        window_title = window_info[3] if len(window_info) > 3 else "Unknown"
        print(f"Will test on window: {window_title}")
        print()
        input("Press Enter to start the test (make sure the Cursor window is visible)...")
        print("Activating Cursor window...")
        run_command(f"wmctrl -ia {window_id}")
        time.sleep(1.5)
        print(f"Moving mouse to ({x}, {y}) and clicking...")
        run_command(f'xdotool mousemove {x} {y}')
        time.sleep(0.5)
        run_command('xdotool click 1')
        time.sleep(0.2)
        run_command('xdotool click 1')
        time.sleep(0.2)
        run_command('xdotool click 1')
        time.sleep(0.5)
        print("Typing test message...")
        run_command('xdotool key ctrl+a')
        time.sleep(0.2)
        run_command('xdotool type "COORDINATE TEST MESSAGE - DID THIS APPEAR IN CHAT?"')
        time.sleep(0.5)
        print("Pressing Enter...")
        run_command('xdotool key Return')
        time.sleep(0.5)
        print()
        print("Did the message 'COORDINATE TEST MESSAGE' appear in the chat?")
        print("1. Yes - coordinates are correct")
        print("2. No, it appeared in the text editor")
        print("3. No, nothing happened")
        print()
        response = input("Enter choice (1/2/3): ").strip()
        if response == "1":
            print("✅ Perfect! Coordinates are working correctly.")
        elif response == "2":
            print("❌ Coordinates are clicking in text editor instead of chat.")
            print("You need to find the exact chat input coordinates.")
            print("Try running: python3 scripts/find_exact_chat_coords.py")
        elif response == "3":
            print("❌ Coordinates might be wrong or chat input not accessible.")
            print("Try adjusting the coordinates in config.json")
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
