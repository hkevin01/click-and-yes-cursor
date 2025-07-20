#!/usr/bin/env python3
"""
Linux window discovery tool using wmctrl.
"""
import subprocess
import json

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def discover_windows_linux():
    print("=== LINUX WINDOW DISCOVERY TOOL ===")
    print("This tool helps you find window titles for your configuration.\n")
    cmd = "wmctrl -l -G"
    stdout, stderr, returncode = run_command(cmd)
    if returncode != 0:
        print(f"Error running wmctrl: {stderr}")
        print("Make sure wmctrl is installed: sudo apt-get install wmctrl")
        return
    lines = stdout.split('\n')
    windows = []
    print(f"Found {len(lines)} windows:\n")
    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue
        parts = line.split(None, 7)
        if len(parts) >= 8:
            window_id = parts[0]
            desktop = parts[1]
            x, y, width, height = parts[2], parts[3], parts[4], parts[5]
            host = parts[6]
            title = parts[7]
            center_x = int(x) + int(width) // 2
            center_y = int(y) + int(height) // 2
            windows.append({
                'id': window_id,
                'title': title,
                'x': center_x,
                'y': center_y,
                'width': int(width),
                'height': int(height)
            })
            print(f"{i:2d}. Title: '{title}'")
            print(f"    ID: {window_id}")
            print(f"    Size: {width}x{height}")
            print(f"    Position: ({x}, {y})")
            print(f"    Center: ({center_x}, {center_y})")
            print()
    interesting_windows = [w for w in windows if w['title'].strip() and not w['title'].startswith('Desktop')]
    print("=== SUGGESTED CONFIG ENTRIES ===")
    print("Add these to your src/config.json windows array:\n")
    config_entries = []
    for i, window in enumerate(interesting_windows[:5]):
        entry = {
            "title": window['title'],
            "coordinates": {"x": window['x'], "y": window['y']},
            "enabled": True
        }
        config_entries.append(entry)
        print(f'  {{')
        print(f'    "title": "{window["title"]}",')
        print(f'    "coordinates": {{"x": {window["x"]}, "y": {window["y"]}}},')
        print(f'    "enabled": true')
        print(f'  }}{"," if i < min(4, len(interesting_windows)-1) else ""}')
    sample_config = {
        "waiting_time": 1.0,
        "cycling": "round_robin",
        "message": [
            "yes, continue",
            "update test plan.md",
            "proceed with changes"
        ],
        "windows": config_entries[:3],
        "window_cycling": "round_robin",
        "fallback_to_coordinates": True
    }
    with open('sample_config_linux.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    print(f"\n=== SAMPLE CONFIG SAVED ===")
    print("A sample configuration has been saved to 'sample_config_linux.json'")
    print("You can copy relevant parts to your src/config.json")

if __name__ == "__main__":
    discover_windows_linux()
