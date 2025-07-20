#!/usr/bin/env python3
"""
Debug script to see exactly what's happening with chat focus
"""
import subprocess
import time
import json
import os

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def log_with_time(msg):
    import datetime
    now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{now} {msg}")

def main():
    print("=== CHAT FOCUS DEBUGGING ===")
    print()
    config_path = os.path.join(os.path.dirname(__file__), '../src/config.json')
    with open(config_path) as f:
        config = json.load(f)
    coords = config['windows'][0]['coordinates']
    chat_x, chat_y = coords['x'], coords['y']
    print(f"Chat coordinates: ({chat_x}, {chat_y})")
    print()
    stdout, _, _ = run_command("wmctrl -l | grep -i cursor | head -1")
    if not stdout:
        print("❌ No Cursor windows found!")
        return
    window_info = stdout.split(None, 3)
    window_id = window_info[0]
    window_title = window_info[3] if len(window_info) > 3 else "Unknown"
    print(f"Testing on: {window_title}")
    print(f"Window ID: {window_id}")
    print()
    input("Press Enter to start debugging (make sure Cursor window is visible)...")
    log_with_time("Step 1: Activating Cursor window")
    run_command(f"wmctrl -ia {window_id}")
    time.sleep(2)
    current_id, _, _ = run_command('xdotool getwindowfocus')
    current_name, _, _ = run_command('xdotool getwindowfocus getwindowname')
    log_with_time(f"Now focused: {current_name.strip()} (ID: {current_id.strip()})")
    log_with_time(f"Step 2: Moving mouse to chat coordinates ({chat_x}, {chat_y})")
    run_command(f'xdotool mousemove {chat_x} {chat_y}')
    time.sleep(1)
    log_with_time("Step 3: Clicking at chat coordinates")
    run_command('xdotool click 1')
    time.sleep(1)
    log_with_time("Step 4: Testing if we can type...")
    run_command('xdotool type "DEBUG TEST MESSAGE"')
    time.sleep(1)
    print("\nDid 'DEBUG TEST MESSAGE' appear in:")
    print("1. The chat input box (GOOD)")
    print("2. The text editor (BAD)")
    print("3. Nowhere (BAD)")
    response = input("\nEnter choice (1/2/3): ").strip()
    if response == "1":
        print("✅ Chat coordinates are working correctly!")
        run_command('xdotool key ctrl+a')
        time.sleep(0.2)
        run_command('xdotool key Delete')
    elif response == "2":
        print("❌ Coordinates are clicking in text editor!")
        print("The coordinates need to be adjusted to point to the chat input.")
        print("Current coordinates:", chat_x, chat_y)
        print()
        print("To fix this:")
        print("1. Manually click in the chat input box")
        print("2. Run: xdotool getmouselocation")
        print("3. Update the coordinates in src/config.json")
    elif response == "3":
        print("❌ Coordinates might be wrong or chat not accessible")
        print("Try different coordinates or check if chat is visible")
    print("\nWould you like to try different coordinates? (y/n)")
    if input().lower() == 'y':
        print("\nMove your mouse to where you want to click and press Enter...")
        input()
        stdout, _, _ = run_command('xdotool getmouselocation')
        print(f"Current mouse location: {stdout}")
        for part in stdout.split():
            if part.startswith('x:'):
                new_x = int(part.split(':')[1])
            elif part.startswith('y:'):
                new_y = int(part.split(':')[1])
        print(f"New coordinates would be: ({new_x}, {new_y})")
        print("Update these in src/config.json if they work better")

if __name__ == "__main__":
    main()
