"""
Script to automate clicking coordinates and copying message from config.json to clipboard.
"""
import datetime
import json
import logging
import os
import platform
import random
import time
from logging.handlers import RotatingFileHandler

import pyautogui
import pyperclip


def get_config():
    """Reads coordinates and message(s) from config file."""
    try:
        with open(os.path.join(os.path.dirname(__file__), '../src/config.json'), encoding='utf-8') as f:
            config = json.load(f)
            coords = config.get('coordinates', {'x': 100, 'y': 200})
            messages = config.get('message', ["yes, continue"])
            cycling = config.get('cycling', 'round_robin')  # 'round_robin', 'random', or 'weighted'
            return coords, messages, cycling
    except Exception as e:
        print(f"Error reading config: {e}")
        return {'x': 100, 'y': 200}, ["yes, continue"], 'round_robin'


def get_next_message(messages, cycling):
    """Cycles or randomly selects messages, supports weights if present."""
    idx_file = os.path.join(os.path.dirname(__file__), '../logs/message_index.txt')
    # If messages are dicts with 'text', support weighted/random cycling
    if isinstance(messages[0], dict):
        if cycling == 'random':
            return random.choice(messages)['text']
        elif cycling == 'weighted':
            weights = [m.get('weight', 1) for m in messages]
            return random.choices(messages, weights=weights, k=1)[0]['text']
        # Default: round robin
        try:
            if os.path.exists(idx_file):
                with open(idx_file, 'r') as f:
                    idx = int(f.read().strip())
            else:
                idx = 0
        except Exception:
            idx = 0
        message = messages[idx % len(messages)]['text']
        try:
            with open(idx_file, 'w') as f:
                f.write(str((idx + 1) % len(messages)))
        except Exception as e:
            print(f"Error writing message index: {e}")
        return message
    # If messages are strings, fallback to round robin
    try:
        if os.path.exists(idx_file):
            with open(idx_file, 'r') as f:
                idx = int(f.read().strip())
        else:
            idx = 0
    except Exception:
        idx = 0
    message = messages[idx % len(messages)]
    try:
        with open(idx_file, 'w') as f:
            f.write(str((idx + 1) % len(messages)))
    except Exception as e:
        print(f"Error writing message index: {e}")
    return message


def log_with_time(msg):
    now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{now} {msg}")
    logging.info(f"{now} {msg}")


def click_and_paste(x, y, message, max_retries=3):
    """Clicks at the given coordinates and pastes the message from clipboard."""
    for attempt in range(max_retries):
        try:
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0.1
            now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            full_message = f"{now} {message}"
            log_with_time(f"[AUTOMATION] Attempt {attempt + 1}: Moving mouse and clicking at ({x}, {y})")
            pyautogui.moveTo(x, y, duration=0.2)
            time.sleep(0.1)
            pyautogui.click(x, y)
            time.sleep(0.5)
            pyperclip.copy(full_message)
            time.sleep(0.1)
            clipboard_content = pyperclip.paste()
            if clipboard_content != full_message:
                log_with_time(f"[WARNING] Clipboard verification failed on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.2)
            pyautogui.press('enter')
            log_with_time(f"[AUTOMATION] Completed successfully on attempt {attempt + 1}")
            return True
        except Exception as err:
            log_with_time(f"[ERROR] Attempt {attempt + 1} failed: {err}")
            if attempt < max_retries - 1:
                log_with_time(f"[RETRY] Waiting 2 seconds before retry...")
                time.sleep(2)
            else:
                log_with_time(f"[FAILED] All {max_retries} attempts failed")
                return False
    return False


def check_platform_dependencies():
    os_name = platform.system()
    missing = []
    if os_name == 'Linux':
        # pyautogui on Linux may require scrot and python3-tk
        import shutil
        if shutil.which('scrot') is None:
            missing.append('scrot (install with: sudo apt-get install scrot)')
        try:
            import tkinter
        except ImportError:
            missing.append('python3-tk (install with: sudo apt-get install python3-tk)')
    if os_name == 'Windows':
        # No extra requirements, but check pyautogui/pyperclip
        try:
            import pyautogui
            import pyperclip
        except ImportError:
            missing.append('pyautogui and pyperclip (install with: pip install pyautogui pyperclip)')
    if os_name == 'Darwin':
        # macOS: pyautogui/pyperclip should work, but may need permissions
        try:
            import pyautogui
            import pyperclip
        except ImportError:
            missing.append('pyautogui and pyperclip (install with: pip3 install pyautogui pyperclip)')
    if missing:
        print("[ERROR] Missing dependencies for platform {}: ".format(os_name))
        for m in missing:
            print("  - " + m)
        print("Please install the missing dependencies and try again.")
        exit(1)


def run_plugins(message, coords):
    import glob
    import importlib.util
    import sys
    plugins_dir = os.path.join(os.path.dirname(__file__), '../plugins')
    if not os.path.isdir(plugins_dir):
        return
    for plugin_path in glob.glob(os.path.join(plugins_dir, '*.py')):
        plugin_name = os.path.splitext(os.path.basename(plugin_path))[0]
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        if spec is None:
            continue
        plugin = importlib.util.module_from_spec(spec)
        try:
            sys.modules[plugin_name] = plugin
            spec.loader.exec_module(plugin)
            if hasattr(plugin, 'run'):
                plugin.run(message=message, coords=coords)
        except Exception as e:
            print(f"[PLUGIN ERROR] {plugin_name}: {e}")


if __name__ == "__main__":
    try:
        check_platform_dependencies()
        log_path = os.path.join(
            os.path.dirname(__file__), '../logs/click_and_type.log'
        )
        handler = RotatingFileHandler(
            log_path, maxBytes=1000000, backupCount=3
        )
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            handlers=[handler]
        )
        coords, messages, cycling = get_config()
        message = get_next_message(messages, cycling)
        log_with_time(f"[AUTOMATION] Starting automation with message: {message[:50]}...")
        run_plugins(message, coords)
        click_and_paste(coords['x'], coords['y'], message)
        log_with_time("[AUTOMATION] Script completed successfully")
    except Exception as e:
        log_with_time(f"[AUTOMATION ERROR] Script failed: {e}")
        exit(1)
