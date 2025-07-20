#!/usr/bin/env python3
"""
Comprehensive Linux window tools test for automation setup.
"""
import subprocess
import sys
import shutil

def run(cmd):
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode

def main():
    print("=== TOOL VERSION CHECKS ===")
    for tool in ["wmctrl", "xdotool", "xprop", "scrot"]:
        path = shutil.which(tool)
        print(f"{tool}: {path if path else 'NOT FOUND'}")
        if path:
            run(f"{tool} --version" if tool != "xprop" else f"{tool} -version")
    print("\n=== PYTHON3-TK CHECK ===")
    try:
        import tkinter
        print("python3-tk: AVAILABLE")
    except ImportError:
        print("python3-tk: NOT AVAILABLE")
    print("\n=== WMCTRL WINDOW LIST ===")
    run("wmctrl -l")
    print("\n=== XPROP TEST ===")
    # Try to get properties of root window
    run("xprop -root")
    print("\n=== SCROT TEST ===")
    run("scrot /tmp/test_screenshot.png")
    print("\n=== XDOTOL TEST ===")
    run("xdotool getmouselocation")
    print("\n=== ALL TESTS COMPLETE ===")

if __name__ == "__main__":
    main()
