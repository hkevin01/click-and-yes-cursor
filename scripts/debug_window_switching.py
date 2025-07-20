#!/usr/bin/env python3
"""
Debug window switching to see why Cursor windows aren't activating
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

def get_current_window():
    current_id, _, _ = run_command('xdotool getwindowfocus')
    current_name, _, _ = run_command('xdotool getwindowfocus getwindowname')
    return current_id.strip(), current_name.strip()

def main():
    print("=== WINDOW SWITCHING DEBUG ===")
    print()
    stdout, _, _ = run_command("wmctrl -l")
    cursor_windows = []
    print("All windows:")
    for line in stdout.split('\n'):
        if line.strip():
            parts = line.split(None, 3)
            if len(parts) >= 4:
                window_id, desktop, host, window_title = parts[0], parts[1], parts[2], parts[3]
                print(f"  {window_id} - {window_title}")
                if 'cursor' in window_title.lower():
                    cursor_windows.append({
                        'id': window_id,
                        'title': window_title
                    })
    print(f"\nFound {len(cursor_windows)} Cursor windows:")
    for i, window in enumerate(cursor_windows):
        print(f"  {i+1}. {window['id']} - {window['title']}")
    if not cursor_windows:
        print("❌ No Cursor windows found!")
        return
    print()
    current_id, current_name = get_current_window()
    print(f"Currently focused: {current_name} (ID: {current_id})")
    print("\n=== TESTING WINDOW ACTIVATION METHODS ===")
    for i, window in enumerate(cursor_windows):
        window_id = window['id']
        window_title = window['title']
        print(f"\n--- Testing Window {i+1}: {window_title} ---")
        print(f"Target ID: {window_id}")
        print("Method 1: wmctrl -ia")
        run_command(f"wmctrl -ia {window_id}")
        time.sleep(1.5)
        new_id, new_name = get_current_window()
        if new_id == window_id:
            print(f"✅ SUCCESS with wmctrl -ia: {new_name}")
        else:
            print(f"❌ FAILED with wmctrl -ia. Got: {new_name} (ID: {new_id})")
            print("Method 2: xdotool windowactivate")
            run_command(f"xdotool windowactivate {window_id}")
            time.sleep(1.5)
            new_id, new_name = get_current_window()
            if new_id == window_id:
                print(f"✅ SUCCESS with xdotool: {new_name}")
            else:
                print(f"❌ FAILED with xdotool. Got: {new_name} (ID: {new_id})")
                print("Method 3: windowraise + windowfocus")
                run_command(f"xdotool windowraise {window_id}")
                time.sleep(0.5)
                run_command(f"xdotool windowfocus {window_id}")
                time.sleep(1.5)
                new_id, new_name = get_current_window()
                if new_id == window_id:
                    print(f"✅ SUCCESS with raise+focus: {new_name}")
                else:
                    print(f"❌ FAILED with raise+focus. Got: {new_name} (ID: {new_id})")
                    print("Method 4: Getting window geometry and clicking")
                    stdout, _, _ = run_command(f"xdotool getwindowgeometry {window_id}")
                    if stdout:
                        try:
                            lines = stdout.split('\n')
                            for line in lines:
                                if 'Position:' in line:
                                    pos = line.split('Position: ')[1].split(' ')[0]
                                    x, y = map(int, pos.split(','))
                                    click_x = x + 100
                                    click_y = y + 30
                                    print(f"Clicking at ({click_x}, {click_y})")
                                    run_command(f'xdotool mousemove {click_x} {click_y}')
                                    time.sleep(0.3)
                                    run_command('xdotool click 1')
                                    time.sleep(1.5)
                                    new_id, new_name = get_current_window()
                                    if new_id == window_id:
                                        print(f"✅ SUCCESS with click: {new_name}")
                                    else:
                                        print(f"❌ FAILED with click. Got: {new_name} (ID: {new_id})")
                                    break
                        except Exception as e:
                            print(f"❌ Click method failed: {e}")
        print(f"Final result: {get_current_window()[1]}")
        if i < len(cursor_windows) - 1:
            input(f"\nPress Enter to test next window...")
    print("\n=== SUMMARY ===")
    print("Which methods worked for switching between Cursor windows?")
    print("This will help us fix the automation.")

if __name__ == "__main__":
    main()
