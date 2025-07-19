#!/usr/bin/env python3
"""
Dry run test - simulates automation without actual clicking
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))

from click_and_type import get_config, get_next_message, log_with_time

def dry_run_click_and_paste(x, y, message):
    """Simulated click and paste for testing"""
    log_with_time(f"[DRY RUN] Would click at ({x}, {y})")
    log_with_time(f"[DRY RUN] Would paste message: {message[:50]}...")
    log_with_time(f"[DRY RUN] Simulation completed successfully")
    return True

if __name__ == "__main__":
    try:
        print("=== DRY RUN TEST ===")
        coords, messages, cycling = get_config()

        # Test 3 message cycles
        for i in range(3):
            message = get_next_message(messages, cycling)
            print(f"\n--- Cycle {i+1} ---")
            success = dry_run_click_and_paste(coords['x'], coords['y'], message)
            if success:
                print(f"✓ Cycle {i+1} completed successfully")
            else:
                print(f"✗ Cycle {i+1} failed")

        print("\n=== DRY RUN COMPLETED ===")

    except Exception as e:
        print(f"✗ DRY RUN FAILED: {e}")
        sys.exit(1)
