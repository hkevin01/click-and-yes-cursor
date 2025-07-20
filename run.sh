#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
CONFIG_FILE="$SCRIPT_DIR/src/config.json"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/run.log"

mkdir -p "$LOG_DIR"

log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

cleanup() {
    log "${RED}Cleaning up: killing all related python processes...${NC} (SIGINT/SIGTERM received)"
    pkill -f scripts/click_and_type.py 2>/dev/null
    pkill -f scripts/gui_config.py 2>/dev/null
    pkill -f "python.*click_and_type.py" 2>/dev/null
    pkill -f "python.*gui_config.py" 2>/dev/null
    ps aux | grep python | grep "$SCRIPT_DIR" | awk '{print $2}' | xargs -r kill -9
    sleep 1
    log "${RED}Script exited at $(date '+%Y-%m-%d %H:%M:%S') due to Ctrl+C or termination.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

pkill -f scripts/click_and_type.py 2>/dev/null

LAST_CYCLE_TIME=$(date +%s)
LOOP_COUNT=0
while true; do
    LOOP_COUNT=$((LOOP_COUNT+1))
    log "${CYAN}[DEBUG] Starting loop iteration $LOOP_COUNT${NC}"

    WAITING_TIME=$(jq -r '.waiting_time // 3' "$CONFIG_FILE" 2>/dev/null)
    if ! [[ "$WAITING_TIME" =~ ^[0-9.]+$ ]]; then
        log "${RED}Invalid or missing waiting_time. Defaulting to 3 minutes.${NC}"
        WAITING_TIME=3
    fi

    SLEEP_SECONDS=$(echo "$WAITING_TIME * 60" | bc 2>/dev/null)
    SLEEP_SECONDS=$(printf "%.0f" "$SLEEP_SECONDS")
    if ! [[ "$SLEEP_SECONDS" =~ ^[0-9]+$ ]]; then
        log "${RED}bc failed to calculate sleep seconds. Defaulting to 180 seconds.${NC}"
        SLEEP_SECONDS=180
    fi

    log "Will sleep for $SLEEP_SECONDS seconds (waiting_time=$WAITING_TIME)"
    log "${CYAN}[DEBUG] WAITING_TIME=$WAITING_TIME, SLEEP_SECONDS=$SLEEP_SECONDS${NC}"

    CYCLE_START_TIME=$(date +%s)
    log "${MAGENTA}==================== AUTOMATION RUN ===================="
    log "${YELLOW}Coordinates and message found. Killing any prior automation instances...${NC}"
    pkill -f scripts/click_and_type.py 2>/dev/null
    sleep 1
    log "${GREEN}Running automation script...${NC}"

    OUTPUT_FILE="$LOG_DIR/python_output.tmp"
    python3 scripts/click_and_type_multi_linux.py > "$OUTPUT_FILE" 2>&1
    PYTHON_EXIT_CODE=$?

    if [ -f "$OUTPUT_FILE" ]; then
        while IFS= read -r line; do
            echo "$line"
            echo "$(date '+%Y-%m-%d %H:%M:%S') $line" >> "$LOG_FILE"
        done < "$OUTPUT_FILE"
        rm -f "$OUTPUT_FILE"
    fi

    if [ $PYTHON_EXIT_CODE -ne 0 ]; then
        log "${RED}[ERROR] Python script failed with exit code $PYTHON_EXIT_CODE${NC}"
    fi

    log "${YELLOW}Waiting $WAITING_TIME minutes before next run... (Press Ctrl+C to exit)${NC}"
    log "${CYAN}[DEBUG] About to sleep for $SLEEP_SECONDS seconds.${NC}"
    sleep $SLEEP_SECONDS

    log "${CYAN}[DEBUG] Woke up from sleep, continuing loop.${NC}"
    CYCLE_END_TIME=$(date +%s)
    ELAPSED=$((CYCLE_END_TIME - CYCLE_START_TIME))
    log "Actual elapsed time this cycle: ${ELAPSED}s"
    DIFF=$((CYCLE_END_TIME - LAST_CYCLE_TIME))
    log "Time since last cycle: ${DIFF}s"
    LAST_CYCLE_TIME=$CYCLE_END_TIME
    log "${CYAN}[DEBUG] End of loop iteration $LOOP_COUNT${NC}"
done
