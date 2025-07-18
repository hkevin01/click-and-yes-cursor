#!/bin/bash
set -x  # Enable debug output
set -e  # Exit on any error (optional, for debugging)
# Run the automation script or GUI config based on config.json, every X minutes in a loop

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
CONFIG_FILE="$SCRIPT_DIR/src/config.json"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/run.log"

mkdir -p "$LOG_DIR"

cleanup() {
    echo "\nCleaning up: killing any background click_and_type.py processes..."
    pkill -f scripts/click_and_type.py 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Kill any background processes before starting
pkill -f scripts/click_and_type.py 2>/dev/null

LAST_CYCLE_TIME=$(date +%s)
while true; do
    WAITING_TIME=$(jq -r '.waiting_time // 3' "$CONFIG_FILE" 2>/dev/null)
    echo "Current wait time is $WAITING_TIME minutes. Press Ctrl+C to exit at any time."
    echo "$(date '+%Y-%m-%d %H:%M:%S') Current wait time is $WAITING_TIME minutes. Press Ctrl+C to exit at any time." >> "$LOG_FILE"
    # Log the actual sleep duration
    SLEEP_SECONDS=$(echo "$WAITING_TIME * 60" | bc)
    echo "WAITING_TIME value: $WAITING_TIME" | tee -a "$LOG_FILE"
    echo "Calculated sleep seconds: $SLEEP_SECONDS" | tee -a "$LOG_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') Will sleep for $SLEEP_SECONDS seconds (waiting_time=$WAITING_TIME)" >> "$LOG_FILE"
    CYCLE_START_TIME=$(date +%s)
    if ! grep -q '"coordinates"' "$CONFIG_FILE" || ! grep -q '"x"' "$CONFIG_FILE" || ! grep -q '"y"' "$CONFIG_FILE"; then
        echo "No coordinates found in config.json. Launching GUI config..."
        python3 "$SCRIPT_DIR/scripts/gui_config.py"
    else
        MESSAGE=$(jq -r '.message' "$CONFIG_FILE")
        if [ "$MESSAGE" == "null" ] || [ -z "$MESSAGE" ]; then
            echo "No message found in config.json. Launching GUI config..."
            python3 "$SCRIPT_DIR/scripts/gui_config.py"
        else
            echo "==================== $(date '+%Y-%m-%d %H:%M:%S') AUTOMATION RUN ===================="
            echo "==================== $(date '+%Y-%m-%d %H:%M:%S') AUTOMATION RUN ====================" >> "$LOG_FILE"
            echo "Coordinates and message found. Killing any prior automation instances..." | tee -a "$LOG_FILE"
            echo "$(date '+%Y-%m-%d %H:%M:%S') Killing any prior automation instances..." >> "$LOG_FILE"
            pkill -f scripts/click_and_type.py 2>/dev/null
            sleep 1
            echo "Running automation script..." | tee -a "$LOG_FILE"
            echo "$(date '+%Y-%m-%d %H:%M:%S') Running automation script..." >> "$LOG_FILE"
            python3 "$SCRIPT_DIR/scripts/click_and_type.py" | tee -a "$LOG_FILE"
        fi
    fi
    WAITING_TIME=$(jq -r '.waiting_time // 3' "$CONFIG_FILE" 2>/dev/null)
    SLEEP_SECONDS=$(echo "$WAITING_TIME * 60" | bc)
    echo "Waiting $WAITING_TIME minutes ($SLEEP_SECONDS seconds) before next run... (Press Ctrl+C to exit)" | tee -a "$LOG_FILE"
    if [[ -n "$WAITING_TIME" && "$WAITING_TIME" =~ ^[0-9.]+$ && -n "$SLEEP_SECONDS" && "$SLEEP_SECONDS" =~ ^[0-9.]+$ ]]; then
        sleep "$SLEEP_SECONDS"
        echo "Slept for $SLEEP_SECONDS seconds, continuing loop..." | tee -a "$LOG_FILE"
    else
        echo "Invalid or missing waiting_time. Defaulting to 180 seconds." | tee -a "$LOG_FILE"
        sleep 180
        echo "Slept for default 180 seconds, continuing loop..." | tee -a "$LOG_FILE"
    fi
    CYCLE_END_TIME=$(date +%s)
    ELAPSED=$((CYCLE_END_TIME - CYCLE_START_TIME))
    echo "$(date '+%Y-%m-%d %H:%M:%S') Actual elapsed time this cycle: ${ELAPSED}s" >> "$LOG_FILE"
    # Optionally, log the time since the last cycle
    DIFF=$((CYCLE_END_TIME - LAST_CYCLE_TIME))
    echo "$(date '+%Y-%m-%d %H:%M:%S') Time since last cycle: ${DIFF}s" >> "$LOG_FILE"
    LAST_CYCLE_TIME=$CYCLE_END_TIME

done
