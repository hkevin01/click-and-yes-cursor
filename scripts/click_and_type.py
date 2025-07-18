"""
Script to automate clicking coordinates and copying message from config.json to clipboard.
"""
import datetime
import json
import logging
import os
import time
from logging.handlers import RotatingFileHandler

import pyautogui
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
        now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        full_message = f"{now} {message}"
        print(f"[AUTOMATION] Moving mouse and clicking at ({x}, {y})")
        logging.info(
            f"Moving mouse and clicking at ({x}, {y})"
        )
        pyautogui.click(x, y)
        time.sleep(0.5)
        pyperclip.copy(full_message)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
    except Exception as err:
        print(f"Automation error: {err}")
        logging.error(f"Automation error: {err}")


if __name__ == "__main__":
    # Set up logging
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

    coords, message = get_config()
    click_and_paste(coords['x'], coords['y'], message)
