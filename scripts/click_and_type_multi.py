"""
Multi-window automation script that cycles between different windows
and sends messages to each one.
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

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False
    print("[WARNING] pygetwindow not available. Install with: pip3 install pygetwindow")


def get_config():
    """Reads configuration including windows and messages."""
    try:
        with open(os.path.join(os.path.dirname(__file__), '../src/config.json'), encoding='utf-8') as f:
            config = json.load(f)

            # Legacy support - convert old format to new format
            if 'coordinates' in config and 'windows' not in config:
                coords = config.get('coordinates', {'x': 100, 'y': 200})
                config['windows'] = [{
                    'title': 'Default Window',
                    'coordinates': coords,
                    'enabled': True
                }]

            windows = config.get('windows', [])
            messages = config.get('message', ["yes, continue"])
            cycling = config.get('cycling', 'round_robin')
            window_cycling = config.get('window_cycling', 'round_robin')
            fallback_to_coordinates = config.get('fallback_to_coordinates', True)

            return windows, messages, cycling, window_cycling, fallback_to_coordinates
    except Exception as e:
        print(f"Error reading config: {e}")
        default_window = {'title': 'Default', 'coordinates': {'x': 100, 'y': 200}, 'enabled': True}
        return [default_window], ["yes, continue"], 'round_robin', 'round_robin', True


def get_next_window(windows, window_cycling):
    """Get the next window to target."""
    enabled_windows = [w for w in windows if w.get('enabled', True)]
    if not enabled_windows:
        return None

    idx_file = os.path.join(os.path.dirname(__file__), '../logs/window_index.txt')

    if window_cycling == 'random':
        return random.choice(enabled_windows)

    # Round robin (default)
    try:
        if os.path.exists(idx_file):
            with open(idx_file, 'r') as f:
                idx = int(f.read().strip())
        else:
            idx = 0
    except Exception:
        idx = 0

    window = enabled_windows[idx % len(enabled_windows)]

    try:
        with open(idx_file, 'w') as f:
            f.write(str((idx + 1) % len(enabled_windows)))
    except Exception as e:
        print(f"Error writing window index: {e}")

    return window


def get_next_message(messages, cycling):
    """Get the next message to send."""
    idx_file = os.path.join(os.path.dirname(__file__), '../logs/message_index.txt')

    if isinstance(messages[0], dict):
        if cycling == 'random':
            return random.choice(messages)['text']
        elif cycling == 'weighted':
            weights = [m.get('weight', 1) for m in messages]
            return random.choices(messages, weights=weights, k=1)[0]['text']

    # Handle both dict and string formats
    try:
        if os.path.exists(idx_file):
            with open(idx_file, 'r') as f:
                idx = int(f.read().strip())
        else:
            idx = 0
    except Exception:
        idx = 0

    if isinstance(messages[0], dict):
        message = messages[idx % len(messages)]['text']
    else:
        message = messages[idx % len(messages)]

    try:
        with open(idx_file, 'w') as f:
            f.write(str((idx + 1) % len(messages)))
    except Exception as e:
        print(f"Error writing message index: {e}")

    return message


def find_window_by_title(title):
    """Find window by title using pygetwindow."""
    if not PYGETWINDOW_AVAILABLE:
        return None

    try:
        # Try exact match first
        windows = gw.getWindowsWithTitle(title)
        if windows:
            return windows[0]

        # Try partial match
        all_windows = gw.getAllWindows()
        for window in all_windows:
            if title.lower() in window.title.lower():
                return window

        return None
    except Exception as e:
        print(f"Error finding window '{title}': {e}")
        return None


def activate_window(window_config, fallback_to_coordinates=True):
    """Activate a window by title, with coordinate fallback."""
    title = window_config.get('title', '')
    coordinates = window_config.get('coordinates', {})

    log_with_time(f"[WINDOW] Attempting to activate window: {title}")

    # Try to find and activate window by title
    if PYGETWINDOW_AVAILABLE and title:
        window = find_window_by_title(title)
        if window:
            try:
                if window.isMinimized:
                    window.restore()
                window.activate()
                time.sleep(0.5)  # Give window time to activate
                log_with_time(f"[WINDOW] Successfully activated window: {title}")
                return True
            except Exception as e:
                log_with_time(f"[WINDOW] Failed to activate window '{title}': {e}")

    # Fallback to coordinates if window activation failed
    if fallback_to_coordinates and coordinates:
        log_with_time(f"[WINDOW] Using coordinate fallback for window: {title}")
        x, y = coordinates.get('x', 100), coordinates.get('y', 200)
        try:
            pyautogui.click(x, y)
            time.sleep(0.5)
            log_with_time(f"[WINDOW] Clicked at coordinates ({x}, {y}) for window: {title}")
            return True
        except Exception as e:
            log_with_time(f"[WINDOW] Coordinate fallback failed: {e}")

    log_with_time(f"[WINDOW] Failed to activate window: {title}")
    return False


def log_with_time(msg):
    """Log message with timestamp."""
    now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{now} {msg}")
    logging.info(f"{now} {msg}")


def send_message_to_window(window_config, message, max_retries=3):
    """Send message to a specific window."""
    title = window_config.get('title', 'Unknown')
    coordinates = window_config.get('coordinates', {})

    for attempt in range(max_retries):
        try:
            log_with_time(f"[AUTOMATION] Attempt {attempt + 1} for window: {title}")

            # Activate the window
            if not activate_window(window_config, fallback_to_coordinates=True):
                if attempt < max_retries - 1:
                    log_with_time(f"[RETRY] Window activation failed, retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                else:
                    log_with_time(f"[FAILED] Could not activate window: {title}")
                    return False

            # Prepare message with timestamp
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0.1

            now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            full_message = f"{now} {message}"

            # Copy to clipboard and verify
            pyperclip.copy(full_message)
            time.sleep(0.1)

            clipboard_content = pyperclip.paste()
            if clipboard_content != full_message:
                log_with_time(f"[WARNING] Clipboard verification failed for {title} on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue

            # Paste and send
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.2)
            pyautogui.press('enter')

            log_with_time(f"[AUTOMATION] Successfully sent message to {title} on attempt {attempt + 1}")
            return True

        except Exception as err:
            log_with_time(f"[ERROR] Attempt {attempt + 1} failed for window {title}: {err}")
            if attempt < max_retries - 1:
                log_with_time(f"[RETRY] Waiting 2 seconds before retry...")
                time.sleep(2)
            else:
                log_with_time(f"[FAILED] All {max_retries} attempts failed for window: {title}")
                return False

    return False


def list_available_windows():
    """List all available windows for debugging."""
    if not PYGETWINDOW_AVAILABLE:
        log_with_time("[DEBUG] pygetwindow not available, cannot list windows")
        return

    try:
        windows = gw.getAllWindows()
        log_with_time(f"[DEBUG] Found {len(windows)} windows:")
        for i, window in enumerate(windows[:10]):  # Limit to first 10
            log_with_time(f"[DEBUG] {i+1}. '{window.title}' (visible: {window.visible})")
    except Exception as e:
        log_with_time(f"[DEBUG] Error listing windows: {e}")


def check_platform_dependencies():
    """Check for required dependencies."""
    os_name = platform.system()
    missing = []

    # Check basic dependencies
    try:
        import pyautogui
        import pyperclip
    except ImportError:
        missing.append('pyautogui and pyperclip (install with: pip install pyautogui pyperclip)')

    # Check pygetwindow
    if not PYGETWINDOW_AVAILABLE:
        missing.append('pygetwindow (install with: pip install pygetwindow)')

    if os_name == 'Linux':
        import shutil
        if shutil.which('scrot') is None:
            missing.append('scrot (install with: sudo apt-get install scrot)')
        try:
            import tkinter
        except ImportError:
            missing.append('python3-tk (install with: sudo apt-get install python3-tk)')

    if missing:
        print(f"[ERROR] Missing dependencies for platform {os_name}:")
        for m in missing:
            print(f"  - {m}")
        print("Please install the missing dependencies and try again.")
        exit(1)


def run_plugins(message, window_config):
    """Run any available plugins."""
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
                plugin.run(message=message, window=window_config)
        except Exception as e:
            print(f"[PLUGIN ERROR] {plugin_name}: {e}")


if __name__ == "__main__":
    try:
        check_platform_dependencies()

        # Set up logging
        log_path = os.path.join(os.path.dirname(__file__), '../logs/click_and_type.log')
        handler = RotatingFileHandler(log_path, maxBytes=1000000, backupCount=3)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            handlers=[handler]
        )

        # Load configuration
        windows, messages, cycling, window_cycling, fallback_to_coordinates = get_config()

        if not windows:
            log_with_time("[ERROR] No windows configured")
            exit(1)

        # Main loop: cycle through windows and messages
        while True:
            target_window = get_next_window(windows, window_cycling)
            if not target_window:
                log_with_time("[ERROR] No enabled windows found")
                exit(1)
            message = get_next_message(messages, cycling)
            log_with_time(f"[AUTOMATION] Target window: {target_window.get('title', 'Unknown')}")
            log_with_time(f"[AUTOMATION] Message: {message[:50]}...")
            list_available_windows()
            run_plugins(message, target_window)
            success = send_message_to_window(target_window, message)
            if success:
                log_with_time("[AUTOMATION] Message sent successfully")
            else:
                log_with_time("[AUTOMATION] Message send failed")
            time.sleep(float(get_config()[0][0].get('waiting_time', 60)))
    except Exception as e:
        log_with_time(f"[AUTOMATION ERROR] Script failed: {e}")
        exit(1)
