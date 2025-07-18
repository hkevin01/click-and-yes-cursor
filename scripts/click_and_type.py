"""
Script to automate clicking coordinates and typing 'yes, continue'.
"""
import pyautogui
import time
import json
import os


def get_coordinates():
    """Reads coordinates from config file or uses defaults."""
    try:
        with open(os.path.join(os.path.dirname(__file__), '../src/config.json')) as f:
            config = json.load(f)
            return config.get('coordinates', {'x': 100, 'y': 200})
    except Exception:
        return {'x': 100, 'y': 200}


def click_and_type(x, y, message="yes, continue"):
    """Clicks at the given coordinates and types a message."""
    try:
        pyautogui.click(x, y)
        time.sleep(0.5)
        pyautogui.typewrite(message)
        pyautogui.press('enter')
    except Exception as err:
        print(f"Automation error: {err}")


if __name__ == "__main__":
    coords = get_coordinates()
    click_and_type(coords['x'], coords['y'])
