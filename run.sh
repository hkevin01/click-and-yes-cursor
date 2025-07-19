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

cleanup() {
    echo -e "${RED}\nCleaning up: killing all related python processes...${NC}"
    pkill -f scripts/click_and_type.py 2>/dev/null
    pkill -f scripts/gui_config.py 2>/dev/null
    pkill -f "python.*click_and_type.py" 2>/dev/null
    pkill -f "python.*gui_config.py" 2>/dev/null
    ps aux | grep python | grep "$SCRIPT_DIR" | awk '{print $2}' | xargs -r kill -9
    sleep 1
    exit 0
}

trap cleanup SIGINT SIGTERM

pkill -f scripts/click_and_type.py 2>/dev/null

LAST_CYCLE_TIME=$(date +%s)
LOOP_COUNT=0
while true; do
    LOOP_COUNT=$((LOOP_COUNT+1))
    echo -e "${CYAN}[DEBUG] Starting loop iteration $LOOP_COUNT at $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo "[DEBUG] Starting loop iteration $LOOP_COUNT at $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

    WAITING_TIME=$(jq -r '.waiting_time // 3' "$CONFIG_FILE" 2>/dev/null)
    if ! [[ "$WAITING_TIME" =~ ^[0-9.]+$ ]]; then
        echo -e "${RED}Invalid or missing waiting_time. Defaulting to 3 minutes.${NC}" | tee -a "$LOG_FILE"
        WAITING_TIME=3
    fi

    SLEEP_SECONDS=$(echo "$WAITING_TIME * 60" | bc 2>/dev/null)
    if ! [[ "$SLEEP_SECONDS" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}bc failed to calculate sleep seconds. Defaulting to 180 seconds.${NC}" | tee -a "$LOG_FILE"
        SLEEP_SECONDS=180
    fi

    echo "$(date '+%Y-%m-%d %H:%M:%S') Will sleep for $SLEEP_SECONDS seconds (waiting_time=$WAITING_TIME)" | tee -a "$LOG_FILE"
    echo -e "${CYAN}[DEBUG] WAITING_TIME=$WAITING_TIME, SLEEP_SECONDS=$SLEEP_SECONDS${NC}"

    CYCLE_START_TIME=$(date +%s)
    echo -e "${MAGENTA}==================== $(date '+%Y-%m-%d %H:%M:%S') AUTOMATION RUN ===================="
    echo "==================== $(date '+%Y-%m-%d %H:%M:%S') AUTOMATION RUN ====================" | tee -a "$LOG_FILE"
    echo -e "${YELLOW}Coordinates and message found. Killing any prior automation instances...${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') Killing any prior automation instances..." | tee -a "$LOG_FILE"
    pkill -f scripts/click_and_type.py 2>/dev/null
    sleep 1
    echo -e "${GREEN}Running automation script...${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') Running automation script..." | tee -a "$LOG_FILE"

    python3 "$SCRIPT_DIR/scripts/click_and_type.py" | tee -a "$LOG_FILE"
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to run click_and_type.py${NC}" | tee -a "$LOG_FILE"
    fi

    echo -e "${YELLOW}Waiting $WAITING_TIME minutes before next run... (Press Ctrl+C to exit)${NC}"
    echo -e "${CYAN}[DEBUG] About to sleep for $SLEEP_SECONDS seconds.${NC}"
    sleep $SLEEP_SECONDS

    echo -e "${CYAN}[DEBUG] Woke up from sleep, continuing loop.${NC}"
    CYCLE_END_TIME=$(date +%s)
    ELAPSED=$((CYCLE_END_TIME - CYCLE_START_TIME))
    echo "$(date '+%Y-%m-%d %H:%M:%S') Actual elapsed time this cycle: ${ELAPSED}s" | tee -a "$LOG_FILE"
    DIFF=$((CYCLE_END_TIME - LAST_CYCLE_TIME))
    echo "$(date '+%Y-%m-%d %H:%M:%S') Time since last cycle: ${DIFF}s" | tee -a "$LOG_FILE"
    LAST_CYCLE_TIME=$CYCLE_END_TIME
    echo -e "${CYAN}[DEBUG] End of loop iteration $LOOP_COUNT at $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo "[DEBUG] End of loop iteration $LOOP_COUNT at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
done
