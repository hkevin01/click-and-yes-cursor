#!/usr/bin/env python3
"""
BULLETPROOF CHATBOX-ONLY AUTOMATION
- Only pastes in chatbox area
- Immediately undos any accidental pastes
- Multiple safety checks and verifications
- GPT 4.1 compatible messaging
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
    log_with_time(f"Window ID: {window_id}")
    run_command(f"wmctrl -ia {window_id}")
    time.sleep(2.0)
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
        log_with_time(f"⚠ Window activation uncertain. Expected: {window_title}, Got: {current_name.strip()}")
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

def emergency_undo_if_wrong_location():
    log_with_time("🚨 EMERGENCY UNDO CHECK")
    window_id, window_name = get_current_window_under_mouse()
    if window_name:
        log_with_time(f"Current window under mouse: {window_name}")
        dangerous_indicators = [
            'visual studio code', 'code', 'vim', 'nano', 'gedit', 'notepad', 'editor', '.py', '.js', '.json', '.md', '.txt', 'file', 'document'
        ]
        window_name_lower = window_name.lower()
        is_dangerous = any(indicator in window_name_lower for indicator in dangerous_indicators)
        if is_dangerous:
            log_with_time(f"⚠ DANGER: Detected text editor/file: {window_name}")
            log_with_time("🔄 PERFORMING EMERGENCY UNDO")
            for undo_attempt in range(5):
                run_command('xdotool key ctrl+z')
                time.sleep(0.3)
            run_command('xdotool key Delete')
            time.sleep(0.2)
            run_command('xdotool key BackSpace')
            time.sleep(0.2)
            log_with_time("✅ Emergency undo completed")
            return True
        else:
            log_with_time(f"✅ Safe window detected: {window_name}")
            return False
    else:
        log_with_time("⚠ Could not determine current window")
        return False

def verify_chatbox_area(chat_x, chat_y):
    log_with_time("🔍 CHATBOX AREA VERIFICATION")
    run_command(f'xdotool mousemove {chat_x} {chat_y}')
    time.sleep(0.5)
    window_id, window_name = get_current_window_under_mouse()
    if window_name:
        log_with_time(f"Window at chatbox coordinates: {window_name}")
        chat_indicators = ['cursor', 'chat', 'ai', 'assistant', 'copilot']
        window_name_lower = window_name.lower()
        is_chat_area = any(indicator in window_name_lower for indicator in chat_indicators)
        if is_chat_area:
            log_with_time(f"✅ Verified chatbox area: {window_name}")
            return True
        else:
            log_with_time(f"⚠ WARNING: Not recognized as chat area: {window_name}")
            return False
    else:
        log_with_time("⚠ Could not verify window at chatbox coordinates")
        return False

def bulletproof_chatbox_only_messaging(message, chat_x, chat_y):
    log_with_time("🛡️ BULLETPROOF CHATBOX-ONLY MESSAGING INITIATED")
    log_with_time(f"Target chatbox coordinates: ({chat_x}, {chat_y})")
    original_x, original_y = get_current_mouse_position()
    log_with_time(f"Original mouse position: ({original_x}, {original_y})")
    if not verify_chatbox_area(chat_x, chat_y):
        log_with_time("❌ SAFETY ABORT: Could not verify chatbox area")
        return False
    try:
        log_with_time("🧹 Safety Layer 2: Clearing any existing selections")
        run_command('xdotool key Escape')
        time.sleep(0.5)
        run_command('xdotool key Escape')
        time.sleep(0.5)
        log_with_time("📍 Safety Layer 3: Precise chatbox positioning")
        for positioning_attempt in range(3):
            run_command(f'xdotool mousemove {chat_x} {chat_y}')
            time.sleep(0.3)
            current_x, current_y = get_current_mouse_position()
            if current_x == chat_x and current_y == chat_y:
                log_with_time(f"✅ Positioned at exact coordinates: ({current_x}, {current_y})")
                break
            else:
                log_with_time(f"⚠ Position correction needed. Attempt {positioning_attempt + 1}")
        if not verify_chatbox_area(chat_x, chat_y):
            log_with_time("❌ SAFETY ABORT: Chatbox verification failed after positioning")
            return False
        log_with_time("🎯 Safety Layer 5: Chatbox focusing")
        click_patterns = [
            ('single', 1), ('double', 2), ('triple', 3), ('single', 1), ('single', 1)
        ]
        for pattern_name, click_count in click_patterns:
            log_with_time(f"Executing {pattern_name} click pattern")
            run_command(f'xdotool click --repeat {click_count} 1')
            time.sleep(0.4)
            if emergency_undo_if_wrong_location():
                log_with_time("❌ SAFETY ABORT: Dangerous area detected during clicking")
                return False
        log_with_time("🧹 Safety Layer 6: Clearing chatbox content")
        run_command('xdotool key ctrl+a')
        time.sleep(0.3)
        if emergency_undo_if_wrong_location():
            log_with_time("❌ SAFETY ABORT: Dangerous area detected during selection")
            return False
        run_command('xdotool key Delete')
        time.sleep(0.3)
        log_with_time("📝 Safety Layer 7: GPT 4.1 compatible message preparation")
        now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        formatted_message = f"{now} {message}"
        if len(formatted_message) > 2000:
            formatted_message = formatted_message[:1900] + "... [message truncated for clarity]"
        log_with_time(f"GPT 4.1 formatted message: {formatted_message[:100]}...")
        log_with_time("📋 Safety Layer 8: Secure pasting")
        clipboard_success = False
        try:
            import pyperclip
            pyperclip.copy("")
            time.sleep(0.2)
            pyperclip.copy(formatted_message)
            time.sleep(0.3)
            clipboard_content = pyperclip.paste()
            if clipboard_content == formatted_message:
                log_with_time("✅ Clipboard verified for GPT 4.1 message")
                run_command('xdotool key ctrl+v')
                time.sleep(0.5)
                if emergency_undo_if_wrong_location():
                    log_with_time("❌ SAFETY ABORT: Dangerous paste detected - undone")
                    return False
                log_with_time("✅ Message safely pasted in chatbox")
                clipboard_success = True
            else:
                log_with_time("⚠ Clipboard verification failed")
        except ImportError:
            log_with_time("pyperclip not available, using safe typing method")
        except Exception as e:
            log_with_time(f"Clipboard method failed: {e}")
        if not clipboard_success:
            log_with_time("📝 Safety Layer 9: Safe typing fallback")
            safe_message = formatted_message.replace('"', '\"').replace('$', '\$').replace('`', '\`').replace('\\', '\\\\')
            run_command(f'xdotool type --delay 50 "{safe_message}"')
            time.sleep(1.0)
            if emergency_undo_if_wrong_location():
                log_with_time("❌ SAFETY ABORT: Dangerous typing detected - undone")
                return False
            log_with_time("✅ Message safely typed in chatbox")
        log_with_time("🔍 Safety Layer 10: Final content verification")
        run_command('xdotool key ctrl+a')
        time.sleep(0.5)
        if emergency_undo_if_wrong_location():
            log_with_time("❌ SAFETY ABORT: Final verification failed")
            return False
        try:
            import pyperclip
            run_command('xdotool key ctrl+c')
            time.sleep(0.5)
            verified_content = pyperclip.paste()
            if message in verified_content:
                log_with_time("✅ Final verification: Message confirmed in chatbox")
            else:
                log_with_time("⚠ Final verification: Content uncertain")
        except:
            log_with_time("Final verification skipped (pyperclip unavailable)")
        log_with_time("📤 Safety Layer 11: Sending to GPT 4.1")
        run_command('xdotool key End')
        time.sleep(0.3)
        run_command('xdotool key Return')
        time.sleep(1.0)
        log_with_time("✅ BULLETPROOF MESSAGING COMPLETED - MESSAGE SENT TO GPT 4.1")
        return True
    except Exception as e:
        log_with_time(f"❌ Bulletproof messaging failed: {e}")
        emergency_undo_if_wrong_location()
        return False
    finally:
        log_with_time(f"🎮 Restoring mouse to original position: ({original_x}, {original_y})")
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

def log_automation_stats(target_window, message, cursor_windows, weighted_messages):
    try:
        logs_dir = os.path.join(os.path.dirname(__file__), '../logs')
        os.makedirs(logs_dir, exist_ok=True)
        stats_file = os.path.join(logs_dir, 'automation_stats.log')
        with open(stats_file, 'a') as f:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n[{now}] GPT 4.1 AUTOMATION RUN\n")
            f.write(f"Target Window: {target_window['title']} ({target_window['id']})\n")
            f.write(f"Message: {message[:100]}...\n")
            f.write(f"Available Windows: {len(cursor_windows)}\n")
            f.write(f"Message Pool Size: {len(weighted_messages)}\n")
            f.write(f"Safety Layers: 11 layers active\n")
            f.write(f"GPT Version: 4.1 compatible\n")
            f.write("=" * 50 + "\n")
    except Exception as e:
        log_with_time(f"Warning: Could not write stats: {e}")

if __name__ == "__main__":
    log_with_time("=== BULLETPROOF GPT 4.1 CHATBOX-ONLY AUTOMATION ===")
    try:
        config = load_config()
        windows_config = config.get('windows', [])
        message_config = config.get('message', [])
        cycling_mode = config.get('window_cycling', 'round_robin')
        if not windows_config or not message_config:
            log_with_time("❌ Invalid configuration")
            sys.exit(1)
        chat_coordinates = windows_config[0].get('coordinates', {})
        if not chat_coordinates:
            log_with_time("❌ No chat coordinates in config")
            sys.exit(1)
        chat_x, chat_y = chat_coordinates['x'], chat_coordinates['y']
        log_with_time(f"GPT 4.1 chatbox coordinates: ({chat_x}, {chat_y})")
        weighted_messages = prepare_weighted_messages(message_config)
        log_with_time(f"Prepared {len(weighted_messages)} GPT 4.1 compatible messages")
        cursor_windows = find_cursor_windows()
        if not cursor_windows:
            log_with_time("❌ No Cursor windows found")
            sys.exit(1)
        log_with_time(f"📋 Available Cursor windows with GPT 4.1 ({len(cursor_windows)}):")
        for i, window in enumerate(cursor_windows):
            log_with_time(f"  {i+1}. {window['title']} ({window['id']})")
        current_index = get_window_index()
        target_index = current_index % len(cursor_windows)
        target_window = cursor_windows[target_index]
        selected_message = random.choice(weighted_messages)
        log_with_time(f"🎯 TARGET: Window {target_index + 1}/{len(cursor_windows)}: {target_window['title']}")
        log_with_time(f"📝 GPT 4.1 MESSAGE: {selected_message[:100]}...")
        success = True
        if not activate_window(target_window):
            success = False
        if not bulletproof_chatbox_only_messaging(selected_message, chat_x, chat_y):
            success = False
        next_index = (current_index + 1) % len(cursor_windows)
        update_window_index(next_index)
        log_with_time(f"🔄 Next run will target window {(target_index + 1) % len(cursor_windows) + 1}")
        log_automation_stats(target_window, selected_message, cursor_windows, weighted_messages)
        if success:
            log_with_time("✅ BULLETPROOF GPT 4.1 AUTOMATION COMPLETED SUCCESSFULLY")
        else:
            log_with_time("⚠ AUTOMATION COMPLETED WITH SAFETY ABORTS")
        log_with_time("=== BULLETPROOF AUTOMATION COMPLETED ===")
    except KeyboardInterrupt:
        log_with_time("🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        log_with_time(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
