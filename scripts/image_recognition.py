"""
Advanced automation: image recognition for UI elements using OpenCV.
"""
import cv2
import numpy as np


def find_image_on_screen(template_path, screenshot_path):
    """Finds template image in screenshot and returns coordinates."""
    template = cv2.imread(template_path, 0)
    screenshot = cv2.imread(screenshot_path, 0)
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val > 0.8:
        return max_loc  # (x, y)
    return None

# Example usage (paths must be updated for real use)
if __name__ == "__main__":
    coords = find_image_on_screen('template.png', 'screenshot.png')
    if coords:
        print(f"Found at: {coords}")
    else:
        print("Not found.")
