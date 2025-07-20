#!/usr/bin/env python3
"""
Manual window switching test
"""
import subprocess
import time

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def get_current_window():
    current_id, _, _ = run_command('xdotool getwindowfocus')
    current_name, _, _ = run_command('xdotool getwindowfocus getwindowname')
    return current_id.strip(), current_name.strip()

def main():
    print("=== MANUAL WINDOW SWITCH TEST ===")
    stdout, _, _ = run_command("wmctrl -l | grep -i cursor")
    cursor_windows = []
    for line in stdout.split('\n'):
        if line.strip():
            parts = line.split(None, 3)
            if len(parts) >= 4:
                window_id, desktop, host, window_title = parts[0], parts[1], parts[2], parts[3]
                cursor_windows.append({
                    'id': window_id,
                    'title': window_title
                })
    if not cursor_windows:
        print("❌ No Cursor windows found!")
        return
    print(f"Found {len(cursor_windows)} Cursor windows:")
    for i, window in enumerate(cursor_windows):
        print(f"  {i+1}. {window['title']}")
    current_id, current_name = get_current_window()
    print(f"\nCurrently focused: {current_name}")
    for i, window in enumerate(cursor_windows):
        print(f"\n--- Switching to window {i+1}: {window['title']} ---")
        window_id = window['id']
        print("Trying wmctrl...")
        run_command(f"wmctrl -ia {window_id}")
        time.sleep(2)
        print("Trying xdotool activate...")
        run_command(f"xdotool windowactivate {window_id}")
        time.sleep(1)
        print("Trying raise + focus...")
        run_command(f"xdotool windowraise {window_id}")
        time.sleep(0.5)
        run_command(f"xdotool windowfocus {window_id}")
        time.sleep(1)
        new_id, new_name = get_current_window()
        if new_id == window_id:
            print(f"✅ SUCCESS! Now focused on: {new_name}")
        else:
            print(f"❌ FAILED! Still focused on: {new_name}")
            print(f"Expected ID: {window_id}, Got ID: {new_id}")
        input("Press Enter to continue to next window...")

if __name__ == "__main__":
    main()
