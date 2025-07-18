#!/bin/bash
# Run the automation script or GUI config based on config.json, every 3 minutes in a loop

CONFIG_FILE="src/config.json"

while true; do
    if ! grep -q '"coordinates"' "$CONFIG_FILE" || ! grep -q '"x"' "$CONFIG_FILE" || ! grep -q '"y"' "$CONFIG_FILE"; then
        echo "No coordinates found in config.json. Launching GUI config..."
        python3 scripts/gui_config.py
    else
        MESSAGE=$(jq -r '.message' "$CONFIG_FILE")
        if [ "$MESSAGE" == "null" ] || [ -z "$MESSAGE" ]; then
            echo "No message found in config.json. Launching GUI config..."
            python3 scripts/gui_config.py
        else
            echo "Coordinates and message found. Running automation script..."
            python3 scripts/click_and_type.py
        fi
    fi
    echo "Waiting 3 minutes before next run... (Press Ctrl+C to exit)"
    sleep 180

done
