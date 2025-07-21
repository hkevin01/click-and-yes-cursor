#!/usr/bin/env python3
"""
CURSOR AI CHAT AUTOMATION
- Specifically designed for Cursor's AI chat interface
- Bypasses file-based danger detection for Cursor windows
- Targets AI chat input field, not code editor
- Handles Cursor's chat interface properly
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
    """Load config.json exactly as specified - never modify it"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '../src/config.json')
        with open(config_path, encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        log_with_time(f"❌ Config error: {e}")
        sys.exit(1)

def prepare_weighted_messages(message_config):
    """Create weighted message list based on config weights"""
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
    """Find all actual Cursor windows (excluding automation project)"""
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
    """Activate window using wmctrl with verification"""
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

def get_current_window_under_mouse():
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

def cursor_ai_chat_safety_check():
    try:
        window_id, window_name = get_current_window_under_mouse()
        if not window_name:
            log_with_time("⚠ Could not detect window under mouse")
            return False
        window_name_lower = window_name.lower()
        if 'cursor' in window_name_lower:
            log_with_time(f"✅ CURSOR AI CHAT TARGET: {window_name}")
            return False
        truly_dangerous = [
            'terminal', 'console', 'shell', 'bash', 'zsh',
            'vim', 'nvim', 'nano', 'gedit', 'kate',
            'file manager', 'nautilus', 'dolphin',
            'system settings', 'control panel'
        ]
        is_truly_dangerous = any(danger in window_name_lower for danger in truly_dangerous)
        if is_truly_dangerous:
            log_with_time(f"⚠ TRULY DANGEROUS AREA: {window_name}")
            return True
        log_with_time(f"✅ SAFE FOR AI CHAT: {window_name}")
        return False
    except:
        log_with_time("⚠ Safety check error - being cautious")
        return True

def cursor_ai_chat_messaging(message, chat_x, chat_y):
    log_with_time("🤖 CURSOR AI CHAT MESSAGING")
    log_with_time(f"AI Chat message: '{message}'")
    original_x, original_y = get_current_mouse_position()
    now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_message = f"{now} {message}"
    log_with_time(f"Full AI message: '{full_message}'")
    log_with_time(f"Message length: {len(full_message)} characters")
    try:
        log_with_time("📍 Step 1: Navigate to AI chat input coordinates")
        run_command(f'xdotool mousemove {chat_x} {chat_y}')
        time.sleep(0.8)
        current_x, current_y = get_current_mouse_position()
        log_with_time(f"Mouse at AI chat coordinates: ({current_x}, {current_y})")
        if cursor_ai_chat_safety_check():
            log_with_time("❌ ABORT: Dangerous area detected (not Cursor AI chat)")
            return False
        log_with_time("🎯 Step 2: Focus AI chat input field")
        for click_attempt in range(3):
            log_with_time(f"🖱️ AI chat focus click {click_attempt + 1}/3")
            run_command('xdotool click 1')
            time.sleep(1.0)
            if cursor_ai_chat_safety_check():
                log_with_time("❌ ABORT: Dangerous area after click")
                return False
        log_with_time("✅ AI chat input field focused")
        log_with_time("📝 Step 3: INSERT MESSAGE INTO AI CHAT")
        log_with_time("🧹 Clearing AI chat input field")
        run_command('xdotool key ctrl+a')
        time.sleep(0.4)
        run_command('xdotool key Delete')
        time.sleep(0.4)
        message_inserted = False
        try:
            import pyperclip
            log_with_time("📋 AI Chat Method 1: Clipboard insertion")
            pyperclip.copy("")
            time.sleep(0.3)
            pyperclip.copy(full_message)
            time.sleep(0.4)
            clipboard_content = pyperclip.paste()
            if clipboard_content == full_message:
                log_with_time("✅ AI message in clipboard, pasting to chat")
                run_command('xdotool key ctrl+v')
                time.sleep(2.5)
                log_with_time("📋 AI chat clipboard paste completed")
                message_inserted = True
            else:
                log_with_time("❌ AI clipboard verification failed")
        except Exception as e:
            log_with_time(f"⚠ AI clipboard method error: {e}")
        if not message_inserted:
            log_with_time("⌨️ AI Chat Method 2: Direct typing to AI")
            log_with_time("⌨️ Typing message to Cursor AI...")
            for i, char in enumerate(full_message):
                if char in ['"', "'", '\\', '$', '`']:
                    escaped_char = f'\\{char}'
                else:
                    escaped_char = char
                run_command(f'xdotool type "{escaped_char}"')
                time.sleep(0.06)
                if (i + 1) % 15 == 0:
                    log_with_time(f"⌨️ AI chat typing: {i + 1}/{len(full_message)} characters")
            log_with_time("✅ AI message typed into chat")
            message_inserted = True
        if not message_inserted:
            log_with_time("❌ Failed to insert message into AI chat")
            return False
        log_with_time("🚀 Step 4: SEND MESSAGE TO CURSOR AI")
        log_with_time("⏳ AI chat message stabilization: 2.5 seconds")
        time.sleep(2.5)
        log_with_time("📍 Positioning cursor at end of AI message")
        run_command('xdotool key End')
        time.sleep(0.6)
        if cursor_ai_chat_safety_check():
            log_with_time("❌ ABORT: Safety check failed before sending to AI")
            return False
        log_with_time("⏎ SENDING MESSAGE TO CURSOR AI")
        ai_send_methods = [
            ("AI Send 1: Return", "xdotool key Return"),
            ("AI Send 2: End+Return", "xdotool key End && sleep 0.4 && xdotool key Return"),
            ("AI Send 3: Return", "xdotool key Return"),
            ("AI Send 4: Keypad Enter", "xdotool key KP_Enter"),
            ("AI Send 5: Final Return", "xdotool key Return")
        ]
        for method_name, command in ai_send_methods:
            log_with_time(f"⏎ {method_name}")
            run_command(command)
            time.sleep(1.2)
        log_with_time("✅ MESSAGE SENT TO CURSOR AI")
        log_with_time("⏳ Waiting for Cursor AI processing: 2.0 seconds")
        time.sleep(2.0)
        log_with_time("✅ CURSOR AI CHAT MESSAGING COMPLETED")
        log_with_time(f"🤖 Sent to AI: '{message}'")
        log_with_time("⏎ Message sent with multiple methods")
        return True
    except Exception as e:
        log_with_time(f"❌ Cursor AI chat messaging failed: {e}")
        return False
    finally:
        log_with_time(f"🎮 Restoring mouse position: ({original_x}, {original_y})")
        run_command(f'xdotool mousemove {original_x} {original_y}')
        time.sleep(0.3)

def get_window_index():
    index_file = os.path.join(os.path.dirname(__file__), '../logs/window_index.txt')
    try:
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                return int(f.read().strip())
        else:
            return 0
    except:
        return 0

def update_window_index(index):
    index_file = os.path.join(os.path.dirname(__file__), '../logs/window_index.txt')
    try:
        os.makedirs(os.path.dirname(index_file), exist_ok=True)
        with open(index_file, 'w') as f:
            f.write(str(index))
    except Exception as e:
        log_with_time(f"Warning: Could not save index: {e}")

def log_cursor_ai_stats(target_window, message, cursor_windows, weighted_messages, success):
    try:
        logs_dir = os.path.join(os.path.dirname(__file__), '../logs')
        os.makedirs(logs_dir, exist_ok=True)
        stats_file = os.path.join(logs_dir, 'cursor_ai_chat_stats.log')
        with open(stats_file, 'a') as f:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n[{now}] CURSOR AI CHAT AUTOMATION RUN\n")
            f.write(f"SUCCESS: {'YES' if success else 'NO'}\n")
            f.write(f"TARGET: {target_window['title']} ({target_window['id']})\n")
            f.write(f"AI MESSAGE: {message}\n")
            f.write(f"PURPOSE: Cursor AI chat interface\n")
            f.write(f"SAFETY: Cursor-specific (allows AI chat)\n")
            f.write(f"METHOD: AI chat input field targeting\n")
            f.write("=" * 50 + "\n")
    except Exception as e:
        log_with_time(f"Warning: Could not write AI stats: {e}")

if __name__ == "__main__":
    log_with_time("=" * 70)
    log_with_time("CURSOR AI CHAT AUTOMATION")
    log_with_time("🤖 PURPOSE: Send messages to Cursor's AI chat interface")
    log_with_time("🎯 TARGET: AI chat input field, not code editor")
    log_with_time("✅ SAFETY: Allows Cursor, blocks dangerous apps")
    log_with_time("=" * 70)
    try:
        config = load_config()
        windows_config = config.get('windows', [])
        message_config = config.get('message', [])
        if not windows_config or not message_config:
            log_with_time("❌ Invalid configuration")
            sys.exit(1)
        chat_coordinates = windows_config[0].get('coordinates', {})
        if not chat_coordinates:
            log_with_time("❌ No AI chat coordinates in config")
            sys.exit(1)
        chat_x, chat_y = chat_coordinates['x'], chat_coordinates['y']
        log_with_time(f"Cursor AI chat coordinates: ({chat_x}, {chat_y})")
        weighted_messages = prepare_weighted_messages(message_config)
        log_with_time(f"Prepared {len(weighted_messages)} AI message options")
        cursor_windows = find_cursor_windows()
        if not cursor_windows:
            log_with_time("❌ No Cursor windows found")
            sys.exit(1)
        log_with_time(f"📋 Available Cursor windows ({len(cursor_windows)}):")
        for i, window in enumerate(cursor_windows):
            log_with_time(f"  {i+1}. {window['title']}")
        current_index = get_window_index()
        target_index = current_index % len(cursor_windows)
        target_window = cursor_windows[target_index]
        selected_message = random.choice(weighted_messages)
        log_with_time(f"🎯 TARGET CURSOR WINDOW: {target_window['title']}")
        log_with_time(f"🤖 AI MESSAGE: '{selected_message[:80]}...'")
        success = True
        log_with_time("🔄 Step 1: Activate Cursor window")
        if not activate_window(target_window):
            success = False
            log_with_time("❌ Cursor window activation failed")
        if success:
            log_with_time("🔄 Step 2: Send message to Cursor AI chat")
            if not cursor_ai_chat_messaging(selected_message, chat_x, chat_y):
                success = False
                log_with_time("❌ Cursor AI chat messaging failed")
        next_index = (current_index + 1) % len(cursor_windows)
        update_window_index(next_index)
        log_with_time(f"🔄 Next run targets Cursor window {(target_index + 1) % len(cursor_windows) + 1}")
        log_cursor_ai_stats(target_window, selected_message, cursor_windows, weighted_messages, success)
        if success:
            log_with_time("✅ CURSOR AI CHAT AUTOMATION SUCCESSFUL")
            log_with_time("🤖 Message sent to Cursor AI interface")
            log_with_time("⏎ AI chat message delivered")
        else:
            log_with_time("❌ AUTOMATION FAILED")
        log_with_time("=" * 70)
    except KeyboardInterrupt:
        log_with_time("🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        log_with_time(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
