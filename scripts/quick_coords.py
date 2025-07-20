#!/usr/bin/env python3
"""
Quick coordinate finder for chat input
"""
import subprocess
import time
import json
import os

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def main():
    print("=== QUICK COORDINATE FINDER ===")
    print()
    print("1. Open a Cursor window")
    print("2. Click exactly in the chat input box")
    print("3. Press Enter here to capture coordinates")
    print()
    input("Ready? Press Enter...")
    stdout, _, _ = run_command('xdotool getmouselocation')
    print(f"Mouse location: {stdout}")
    x, y = 0, 0
    for part in stdout.split():
        if part.startswith('x:'):
            x = int(part.split(':')[1])
        elif part.startswith('y:'):
            y = int(part.split(':')[1])
    print(f"Coordinates: x={x}, y={y}")
    config_path = os.path.join(os.path.dirname(__file__), '../src/config.json')
    with open(config_path) as f:
        config = json.load(f)
    config['windows'][0]['coordinates'] = {'x': x, 'y': y}
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✅ Updated config.json with coordinates ({x}, {y})")
    print("\nTesting coordinates in 3 seconds...")
    time.sleep(3)
    run_command(f'xdotool mousemove {x} {y}')
    time.sleep(0.5)
    run_command('xdotool click 1')
    time.sleep(0.5)
    run_command('xdotool type "COORDINATE TEST"')
    print("\nDid 'COORDINATE TEST' appear in the chat input? (y/n)")
    if input().lower() == 'y':
        print("✅ Perfect! Coordinates are set correctly.")
    else:
        print("❌ Try again with more precise positioning")

if __name__ == "__main__":
    main()
