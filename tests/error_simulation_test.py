#!/usr/bin/env python3
"""
Test error handling and retry logic
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))

def test_invalid_coordinates():
    """Test with coordinates outside screen bounds"""
    print("=== TESTING INVALID COORDINATES ===")

    # Import here to avoid import issues
    from click_and_type import click_and_paste

    # Test with coordinates way outside screen
    invalid_coords = [
        (-100, -100),  # Negative coordinates
        (99999, 99999),  # Way too large
        (0, 99999),  # Partially invalid
    ]

    for x, y in invalid_coords:
        print(f"\nTesting coordinates ({x}, {y}):")
        try:
            result = click_and_paste(x, y, "test message", max_retries=1)
            print(f"Result: {'Success' if result else 'Failed as expected'}")
        except Exception as e:
            print(f"Exception caught: {e}")

if __name__ == "__main__":
    test_invalid_coordinates()
