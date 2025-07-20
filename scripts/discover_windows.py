#!/usr/bin/env python3
"""
Window discovery tool to help find window titles for configuration.
"""
try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False
    print("pygetwindow not available. Install with: pip3 install pygetwindow")
    exit(1)

def discover_windows():
    """List all available windows with their properties."""
    print("=== WINDOW DISCOVERY TOOL ===")
    print("This tool helps you find window titles for your configuration.\n")

    try:
        windows = gw.getAllWindows()
        visible_windows = [w for w in windows if w.visible and w.title.strip()]

        print(f"Found {len(visible_windows)} visible windows with titles:\n")

        for i, window in enumerate(visible_windows, 1):
            print(f"{i:2d}. Title: '{window.title}'")
            print(f"    Size: {window.width}x{window.height}")
            print(f"    Position: ({window.left}, {window.top})")
            print(f"    Minimized: {window.isMinimized}")
            print(f"    Active: {window.isActive}")
            print()

        print("=== SUGGESTED CONFIG ENTRIES ===")
        print("Add these to your src/config.json windows array:\n")

        for i, window in enumerate(visible_windows[:5]):  # Show first 5
            center_x = window.left + window.width // 2
            center_y = window.top + window.height // 2

            print(f'  {{')
            print(f'    "title": "{window.title}",')
            print(f'    "coordinates": {{"x": {center_x}, "y": {center_y}}},')
            print(f'    "enabled": true')
            print(f'  }}{"," if i < min(4, len(visible_windows)-1) else ""}')

    except Exception as e:
        print(f"Error discovering windows: {e}")

if __name__ == "__main__":
    discover_windows()
