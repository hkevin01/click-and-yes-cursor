#!/bin/bash
set -x  # Enable debug output
# set -e  # Exit on any error (optional, for debugging)
# Run the automation script or GUI config based on config.json, every X minutes in a loop

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
CONFIG_FILE="$SCRIPT_DIR/src/config.json"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/run.log"

mkdir -p "$LOG_DIR"

cleanup() {
    echo "\nCleaning up: killing any background click_and_type.py processes..." | tee -a "$LOG_FILE"
    pkill -f scripts/click_and_type.py 2>/dev/null || true
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] Script exited (cleanup called). If this was unexpected, check for terminal or process manager issues." | tee -a "$LOG_FILE"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Kill any background processes before starting
pkill -f scripts/click_and_type.py 2>/dev/null || true

LAST_CYCLE_TIME=$(date +%s)
LOOP_COUNT=0
while true; do
    LOOP_COUNT=$((LOOP_COUNT+1))
    echo "[DEBUG] Starting loop iteration $LOOP_COUNT at $(date '+%Y-%m-%d %H:%M:%S')"
    echo "[DEBUG] Starting loop iteration $LOOP_COUNT at $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
    WAITING_TIME=$(jq -r '.waiting_time // 3' "$CONFIG_FILE" 2>/dev/null)
    if [ $? -ne 0 ]; then
        echo "[ERROR] jq failed to read waiting_time from $CONFIG_FILE" | tee -a "$LOG_FILE"
    fi
    echo "Current wait time is $WAITING_TIME minutes. Press Ctrl+C to exit at any time."
    echo "$(date '+%Y-%m-%d %H:%M:%S') Current wait time is $WAITING_TIME minutes. Press Ctrl+C to exit at any time." >> "$LOG_FILE"
    SLEEP_SECONDS=$(echo "$WAITING_TIME * 60" | bc 2>/dev/null)
    if [ $? -ne 0 ]; then
        echo "[ERROR] bc failed to calculate sleep seconds from WAITING_TIME=$WAITING_TIME" | tee -a "$LOG_FILE"
        SLEEP_SECONDS=180
    fi
    echo "$(date '+%Y-%m-%d %H:%M:%S') Will sleep for $SLEEP_SECONDS seconds (waiting_time=$WAITING_TIME)" >> "$LOG_FILE"
    echo "[DEBUG] WAITING_TIME=$WAITING_TIME, SLEEP_SECONDS=$SLEEP_SECONDS"
    CYCLE_START_TIME=$(date +%s)
    if ! grep -q '"coordinates"' "$CONFIG_FILE" || ! grep -q '"x"' "$CONFIG_FILE" || ! grep -q '"y"' "$CONFIG_FILE"; then
        echo "No coordinates found in config.json. Launching GUI config..." | tee -a "$LOG_FILE"
        python3 "$SCRIPT_DIR/scripts/gui_config.py"
        if [ $? -ne 0 ]; then
            echo "[ERROR] Failed to run gui_config.py" | tee -a "$LOG_FILE"
        fi
    else
        MESSAGE=$(jq -r '.message' "$CONFIG_FILE")
        if [ "$MESSAGE" == "null" ] || [ -z "$MESSAGE" ]; then
            echo "No message found in config.json. Launching GUI config..." | tee -a "$LOG_FILE"
            python3 "$SCRIPT_DIR/scripts/gui_config.py"
            if [ $? -ne 0 ]; then
                echo "[ERROR] Failed to run gui_config.py" | tee -a "$LOG_FILE"
            fi
        else
            echo "==================== $(date '+%Y-%m-%d %H:%M:%S') AUTOMATION RUN ====================" | tee -a "$LOG_FILE"
            echo "==================== $(date '+%Y-%m-%d %H:%M:%S') AUTOMATION RUN ====================" >> "$LOG_FILE"
            echo "Coordinates and message found. Killing any prior automation instances..." | tee -a "$LOG_FILE"
            echo "$(date '+%Y-%m-%d %H:%M:%S') Killing any prior automation instances..." >> "$LOG_FILE"
            pkill -f scripts/click_and_type.py 2>/dev/null || true
            sleep 1
            echo "Running automation script..." | tee -a "$LOG_FILE"
            echo "$(date '+%Y-%m-%d %H:%M:%S') Running automation script..." >> "$LOG_FILE"
            python3 "$SCRIPT_DIR/scripts/click_and_type.py" 2>&1 | tee -a "$LOG_FILE"
            if [ $? -ne 0 ]; then
                echo "[ERROR] Failed to run click_and_type.py" | tee -a "$LOG_FILE"
            fi
            # Log click event
            echo "$(date '+%Y-%m-%d %H:%M:%S') [EVENT] Click occurred at coordinates: $(jq -r '.coordinates.x' "$CONFIG_FILE"),$(jq -r '.coordinates.y' "$CONFIG_FILE")" | tee -a "$LOG_FILE"
            echo "$(date '+%Y-%m-%d %H:%M:%S') [EVENT] Message pasted: $MESSAGE" | tee -a "$LOG_FILE"
        fi
    fi
    WAITING_TIME=$(jq -r '.waiting_time // 3' "$CONFIG_FILE" 2>/dev/null)
    SLEEP_SECONDS=$(echo "$WAITING_TIME * 60" | bc 2>/dev/null)
    echo "Waiting $WAITING_TIME minutes before next run... (Press Ctrl+C to exit)"
    echo "[DEBUG] About to sleep for $SLEEP_SECONDS seconds."
    if [[ -n "$WAITING_TIME" && "$WAITING_TIME" =~ ^[0-9.]+$ ]]; then
        sleep $SLEEP_SECONDS
        if [ $? -ne 0 ]; then
            echo "[ERROR] sleep command failed" | tee -a "$LOG_FILE"
        fi
    else
        echo "Invalid or missing waiting_time. Defaulting to 180 seconds." | tee -a "$LOG_FILE"
        sleep 180
    fi
    echo "[DEBUG] Woke up from sleep, continuing loop."
    CYCLE_END_TIME=$(date +%s)
    ELAPSED=$((CYCLE_END_TIME - CYCLE_START_TIME))
    echo "$(date '+%Y-%m-%d %H:%M:%S') Actual elapsed time this cycle: ${ELAPSED}s" >> "$LOG_FILE"
    # Optionally, log the time since the last cycle
    DIFF=$((CYCLE_END_TIME - LAST_CYCLE_TIME))
    echo "$(date '+%Y-%m-%d %H:%M:%S') Time since last cycle: ${DIFF}s" >> "$LOG_FILE"
    LAST_CYCLE_TIME=$CYCLE_END_TIME
    echo "[DEBUG] End of loop iteration $LOOP_COUNT at $(date '+%Y-%m-%d %H:%M:%S')"
    echo "[DEBUG] End of loop iteration $LOOP_COUNT at $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

    # Check if running in VS Code terminal and warn user
    if [ "$TERM_PROGRAM" == "vscode" ] || [ "$TERM" == "xterm-256color" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') [WARN] VS Code terminal detected. If automation stops after one run, try running this script in a system terminal, or use 'nohup ./run.sh &' or 'tmux'/'screen' to keep it alive." | tee -a "$LOG_FILE"
    fi

done
