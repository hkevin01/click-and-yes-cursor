"""
Script to automate clicking coordinates and copying message from config.json to clipboard.
"""
import pyautogui
import time
import json
import os
import pyperclip


def get_config():
    """Reads coordinates and message from config file."""
    try:
        with open(os.path.join(os.path.dirname(__file__), '../src/config.json'), encoding='utf-8') as f:
            config = json.load(f)
            coords = config.get('coordinates', {'x': 100, 'y': 200})
            message = config.get('message', 'yes, continue')
            return coords, message
    except Exception as e:
        print(f"Error reading config: {e}")
        return {'x': 100, 'y': 200}, 'yes, continue'


def click_and_paste(x, y, message):
    """Clicks at the given coordinates and pastes the message from clipboard."""
    try:
        pyautogui.click(x, y)
        time.sleep(0.5)
        pyperclip.copy(message)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
    except Exception as err:
        print(f"Automation error: {err}")


if __name__ == "__main__":
    coords, message = get_config()
    click_and_paste(coords['x'], coords['y'], message)
