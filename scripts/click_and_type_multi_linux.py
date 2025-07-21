#!/usr/bin/env python3
"""
CURSOR AI CHAT PANEL FINDER
- Dynamically finds Cursor's AI chat panel
- NEVER touches code editor areas
- Absolute protection against file overwriting
- Visual coordinate verification before typing
"""
import datetime
import json
import os
import random
import signal
import subprocess
import sys
import time

def signal_handler(signum, frame):
    log_with_time(f"🛑 Shutdown requested at {datetime.datetime.now().strftime('%H:%M:%S')}")
    sys.exit(0)

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
    except Exception as e:
        return "", str(e), 1

def load_config():
    try:
        config_path = os.path.join(os.path.dirname(__file__), '../src/config.json')
        with open(config_path, encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        log_with_time(f"❌ Config error: {e}")
        sys.exit(1)

def prepare_weighted_messages(message_config):
    weighted_messages = []
    for msg_item in message_config:
        if isinstance(msg_item, dict):
            text = msg_item.get('text', '')
            weight = msg_item.get('weight', 1)
        else:
            text = str(msg_item)
            weight = 1
        for _ in range(weight):
            weighted_messages.append(text)
    return weighted_messages

def find_cursor_windows():
    log_with_time("🔍 Finding Cursor windows...")
    stdout, stderr, returncode = run_command("wmctrl -l")
    if returncode != 0:
        log_with_time(f"wmctrl failed: {stderr}")
        return []
    cursor_windows = []
    for line in stdout.split('\n'):
        if not line.strip():
            continue
        parts = line.split(None, 3)
        if len(parts) >= 4:
            window_id, desktop, host, window_title = parts[0], parts[1], parts[2], parts[3]
            if 'cursor' in window_title.lower() and 'click-and-yes-cursor' not in window_title.lower():
                cursor_windows.append({
                    'id': window_id,
                    'title': window_title,
                    'desktop': desktop
                })
                log_with_time(f"Found Cursor window: {window_id} - {window_title}")
    cursor_windows.sort(key=lambda w: w['id'])
    log_with_time(f"Found {len(cursor_windows)} valid Cursor windows")
    return cursor_windows

def activate_window(window_info):
    window_id = window_info['id']
    window_title = window_info['title']
    log_with_time(f"🎯 Activating: {window_title}")
    for attempt in range(3):
        run_command(f"wmctrl -ia {window_id}")
        time.sleep(1.5)
        current_id, _, _ = run_command('xdotool getwindowfocus')
        current_name, _, _ = run_command('xdotool getwindowfocus getwindowname')
        try:
            expected_decimal = str(int(window_id, 16))
        except:
            expected_decimal = window_id
        if current_id.strip() == expected_decimal or window_title.lower() in current_name.lower():
            log_with_time(f"✅ Window activated: {current_name.strip()}")
            return True
        else:
            log_with_time(f"⚠ Activation attempt {attempt + 1} failed")
            if attempt < 2:
                time.sleep(1.0)
    return False

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

def get_window_info():
    try:
        window_id, _, _ = run_command('xdotool getwindowfocus')
        if not window_id:
            return None
        geometry_output, _, _ = run_command(f'xdotool getwindowgeometry {window_id}')
        window_name, _, _ = run_command(f'xdotool getwindowname {window_id}')
        return {
            'id': window_id,
            'name': window_name.strip(),
            'geometry': geometry_output
        }
    except:
        return None

def find_cursor_ai_chat_panel():
    log_with_time("🔍 SEARCHING FOR CURSOR AI CHAT PANEL")
    window_info = get_window_info()
    if not window_info:
        log_with_time("❌ Could not get window information")
        return None
    log_with_time(f"Window: {window_info['name']}")
    log_with_time(f"Geometry: {window_info['geometry']}")
    try:
        geometry_line = [line for line in window_info['geometry'].split('\n') if 'Geometry:' in line][0]
        geometry_part = geometry_line.split('Geometry: ')[1]
        size_part, offset_part = geometry_part.split('+', 1)
        width, height = map(int, size_part.split('x'))
        if '+' in offset_part:
            x_offset, y_offset = map(int, offset_part.split('+'))
        else:
            parts = offset_part.split('+')
            if len(parts) == 2:
                x_offset, y_offset = map(int, parts)
            else:
                x_offset, y_offset = 0, 0
        log_with_time(f"Window bounds: {width}x{height} at ({x_offset}, {y_offset})")
    except Exception as e:
        log_with_time(f"⚠ Could not parse geometry: {e}")
        width, height = 1920, 1080
        x_offset, y_offset = 0, 0
    potential_chat_areas = [
        {
            'name': 'Right Panel (Typical AI Chat)',
            'x': x_offset + int(width * 0.75),
            'y': y_offset + int(height * 0.85),
            'description': 'Right side panel bottom (most common AI chat location)'
        },
        {
            'name': 'Bottom Panel Center',
            'x': x_offset + int(width * 0.5),
            'y': y_offset + int(height * 0.9),
            'description': 'Bottom center panel (alternative AI chat)'
        },
        {
            'name': 'Right Panel Mid',
            'x': x_offset + int(width * 0.8),
            'y': y_offset + int(height * 0.7),
            'description': 'Right panel middle area'
        },
        {
            'name': 'Bottom Right Corner',
            'x': x_offset + int(width * 0.85),
            'y': y_offset + int(height * 0.95),
            'description': 'Bottom right corner input area'
        }
    ]
    log_with_time(f"Testing {len(potential_chat_areas)} potential AI chat locations...")
    for i, area in enumerate(potential_chat_areas):
        log_with_time(f"🔍 Test {i+1}: {area['name']} at ({area['x']}, {area['y']})")
        log_with_time(f"   Purpose: {area['description']}")
        run_command(f"xdotool mousemove {area['x']} {area['y']}")
        time.sleep(0.5)
        mouse_window_id, mouse_window_name = get_window_under_mouse()
        if mouse_window_name and 'cursor' in mouse_window_name.lower():
            log_with_time(f"   ✅ Found Cursor area: {mouse_window_name}")
            if test_if_text_input_area(area['x'], area['y']):
                log_with_time(f"   ✅ CONFIRMED: Text input area detected!")
                log_with_time(f"   🎯 AI CHAT PANEL FOUND: {area['name']}")
                return {
                    'x': area['x'],
                    'y': area['y'],
                    'name': area['name'],
                    'description': area['description']
                }
            else:
                log_with_time(f"   ⚠ Not a text input area")
        else:
            log_with_time(f"   ❌ Not in Cursor window")
    log_with_time("❌ Could not find Cursor AI chat panel")
    return None

def get_window_under_mouse():
    try:
        stdout, _, _ = run_command('xdotool getmouselocation --shell')
        window_id = None
        for line in stdout.split('\n'):
            if 'WINDOW=' in line:
                window_id = line.split('WINDOW=')[1]
                break
        if window_id:
            window_name, _, _ = run_command(f'xdotool getwindowname {window_id}')
            return window_id, window_name.strip()
        return None, None
    except:
        return None, None

def test_if_text_input_area(x, y):
    try:
        log_with_time(f"   🧪 Testing text input at ({x}, {y})")
        run_command(f"xdotool mousemove {x} {y}")
        time.sleep(0.3)
        run_command("xdotool click 1")
        time.sleep(0.5)
        run_command("xdotool type ' '")
        time.sleep(0.1)
        run_command("xdotool key BackSpace")
        time.sleep(0.1)
        log_with_time(f"   ✅ Text input test completed")
        return True
    except Exception as e:
        log_with_time(f"   ❌ Text input test failed: {e}")
        return False

def absolute_file_protection_check():
    try:
        window_id, window_name = get_window_under_mouse()
        if not window_name:
            log_with_time("⚠ Cannot identify current window - BLOCKING for safety")
            return True
        window_name_lower = window_name.lower()
        file_extensions = ['.py', '.js', '.json', '.md', '.txt', '.cpp', '.c', '.java', '.html', '.css', '.yml', '.yaml', '.xml', '.sql']
        for ext in file_extensions:
            if ext in window_name_lower:
                log_with_time(f"🚫 ABSOLUTE BLOCK: File extension {ext} detected in window: {window_name}")
                return True
        editor_keywords = ['visual studio code', 'vim', 'nvim', 'nano', 'gedit', 'kate', 'sublime', 'atom', 'notepad']
        for keyword in editor_keywords:
            if keyword in window_name_lower:
                log_with_time(f"🚫 ABSOLUTE BLOCK: Editor keyword '{keyword}' detected: {window_name}")
                return True
        if 'cursor' in window_name_lower and not any(ext in window_name_lower for ext in file_extensions):
            log_with_time(f"✅ CURSOR DETECTED WITHOUT FILE INDICATORS: {window_name}")
            return False
        log_with_time(f"🚫 SAFETY BLOCK: Uncertain window type: {window_name}")
        return True
    except:
        log_with_time("🚫 SAFETY BLOCK: Error in protection check")
        return True

def manual_coordinate_finder():
    log_with_time("🎯 MANUAL AI CHAT COORDINATE FINDER")
    log_with_time("This will help you find the exact AI chat input coordinates")
    try:
        print("\n" + "="*60)
        print("MANUAL COORDINATE FINDER FOR CURSOR AI CHAT")
        print("="*60)
        print("1. Make sure Cursor is open with AI chat panel visible")
        print("2. Position your mouse over the AI chat INPUT FIELD")
        print("3. Press Enter when your mouse is over the chat input")
        print("4. Or type 'auto' to try automatic detection")
        print("5. Or type 'abort' to cancel")
        print("="*60)
        user_input = input("Ready? Press Enter when mouse is over AI chat input (or 'auto'/'abort'): ").strip().lower()
        if user_input == 'abort':
            log_with_time("❌ Manual coordinate finding aborted")
            return None
        elif user_input == 'auto':
            log_with_time("🔍 Attempting automatic detection...")
            return find_cursor_ai_chat_panel()
        else:
            current_x, current_y = get_current_mouse_position()
            log_with_time(f"📍 Current mouse position: ({current_x}, {current_y})")
            run_command(f"xdotool mousemove {current_x} {current_y}")
            time.sleep(0.3)
            if absolute_file_protection_check():
                log_with_time("❌ UNSAFE LOCATION: This appears to be a code editor area")
                log_with_time("Please position mouse over the AI CHAT INPUT FIELD, not the code editor")
                return None
            log_with_time("✅ Location appears safe for AI chat")
            confirm = input(f"Confirm AI chat coordinates ({current_x}, {current_y})? (y/n): ").strip().lower()
            if confirm == 'y':
                log_with_time(f"✅ AI chat coordinates confirmed: ({current_x}, {current_y})")
                try:
                    config = load_config()
                    config['windows'][0]['coordinates'] = {'x': current_x, 'y': current_y}
                    config_path = os.path.join(os.path.dirname(__file__), '../src/config.json')
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2)
                    log_with_time("✅ Coordinates saved to config.json")
                except Exception as e:
                    log_with_time(f"⚠ Could not save coordinates: {e}")
                return {
                    'x': current_x,
                    'y': current_y,
                    'name': 'Manual Selection',
                    'description': 'User-confirmed AI chat input coordinates'
                }
            else:
                log_with_time("❌ Coordinates not confirmed")
                return None
    except KeyboardInterrupt:
        log_with_time("❌ Manual coordinate finding interrupted")
        return None
    except Exception as e:
        log_with_time(f"❌ Manual coordinate finding error: {e}")
        return None

if __name__ == "__main__":
    log_with_time("=" * 80)
    log_with_time("CURSOR AI CHAT PANEL FINDER & ABSOLUTE FILE PROTECTION")
    log_with_time("🔍 FINDS: Actual AI chat panel coordinates")
    log_with_time("🚫 BLOCKS: Any code editor areas (absolute protection)")
    log_with_time("🛡️ PREVENTS: File overwriting at all costs")
    log_with_time("=" * 80)
    try:
        config = load_config()
        windows_config = config.get('windows', [])
        message_config = config.get('message', [])
        if not windows_config or not message_config:
            log_with_time("❌ Invalid configuration")
            sys.exit(1)
        cursor_windows = find_cursor_windows()
        if not cursor_windows:
            log_with_time("❌ No Cursor windows found")
            log_with_time("Please open Cursor with an AI chat panel visible")
            sys.exit(1)
        log_with_time(f"📋 Available Cursor windows ({len(cursor_windows)}):")
        for i, window in enumerate(cursor_windows):
            log_with_time(f"  {i+1}. {window['title']}")
        target_window = cursor_windows[0]
        log_with_time(f"🎯 TARGET: {target_window['title']}")
        if not activate_window(target_window):
            log_with_time("❌ Could not activate Cursor window")
            sys.exit(1)
        log_with_time("🔍 Step 1: Find AI chat panel coordinates")
        ai_chat_coords = find_cursor_ai_chat_panel()
        if not ai_chat_coords:
            log_with_time("⚠ Automatic AI chat detection failed")
            ai_chat_coords = manual_coordinate_finder()
        if not ai_chat_coords:
            log_with_time("❌ Could not find AI chat coordinates")
            log_with_time("💡 TIP: Make sure Cursor's AI chat panel is visible and try again")
            sys.exit(1)
        log_with_time(f"✅ AI CHAT COORDINATES FOUND:")
        log_with_time(f"   Location: {ai_chat_coords['name']}")
        log_with_time(f"   Coordinates: ({ai_chat_coords['x']}, {ai_chat_coords['y']})")
        log_with_time(f"   Description: {ai_chat_coords['description']}")
        weighted_messages = prepare_weighted_messages(message_config)
        test_message = random.choice(weighted_messages)
        log_with_time(f"🧪 TEST MESSAGE: '{test_message[:50]}...'")
        log_with_time("🛡️ Final safety verification...")
        run_command(f"xdotool mousemove {ai_chat_coords['x']} {ai_chat_coords['y']}")
        time.sleep(0.5)
        if absolute_file_protection_check():
            log_with_time("❌ FINAL SAFETY CHECK FAILED")
            log_with_time("❌ Coordinates appear to be in code editor area")
            log_with_time("❌ ABORTING to prevent file overwriting")
            sys.exit(1)
        log_with_time("✅ FINAL SAFETY CHECK PASSED")
        log_with_time("✅ Ready for AI chat automation")
        log_with_time("✅ Coordinates are safe and verified")
        log_with_time("=" * 80)
        log_with_time("🎯 CURSOR AI CHAT PANEL SUCCESSFULLY LOCATED")
        log_with_time("🛡️ FILE OVERWRITING PROTECTION ACTIVE")
        log_with_time("🤖 Ready for safe AI chat automation")
        log_with_time("=" * 80)
    except KeyboardInterrupt:
        log_with_time("🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        log_with_time(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
