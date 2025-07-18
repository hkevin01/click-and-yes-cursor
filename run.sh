#!/bin/bash
set -x
PS4='+ $BASH_SOURCE:$LINENO:${FUNCNAME[0]}: '

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

trap cleanup SIGINT SIGTERM

# Kill any background processes before starting
pkill -f scripts/click_and_type.py 2>/dev/null

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
    # Only run the automation script, do not launch GUI config
    echo "==================== $(date '+%Y-%m-%d %H:%M:%S') AUTOMATION RUN ====================" | tee -a "$LOG_FILE"
    echo "Coordinates and message found. Killing any prior automation instances..." | tee -a "$LOG_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') Killing any prior automation instances..." >> "$LOG_FILE"
    pkill -f scripts/click_and_type.py 2>/dev/null
    sleep 1
    echo "Running automation script..." | tee -a "$LOG_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') Running automation script..." >> "$LOG_FILE"
    python3 "$SCRIPT_DIR/scripts/click_and_type.py" | tee -a "$LOG_FILE"
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to run click_and_type.py" | tee -a "$LOG_FILE"
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
    DIFF=$((CYCLE_END_TIME - LAST_CYCLE_TIME))
    echo "$(date '+%Y-%m-%d %H:%M:%S') Time since last cycle: ${DIFF}s" >> "$LOG_FILE"
    LAST_CYCLE_TIME=$CYCLE_END_TIME
    echo "[DEBUG] End of loop iteration $LOOP_COUNT at $(date '+%Y-%m-%d %H:%M:%S')"
    echo "[DEBUG] End of loop iteration $LOOP_COUNT at $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
done
