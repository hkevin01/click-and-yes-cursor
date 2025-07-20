#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd)"
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
    pkill -f \"python.*click_and_type.py\" 2>/dev/null
    pkill -f \"python.*gui_config.py\" 2>/dev/null
    ps aux | grep python | grep "$SCRIPT_DIR" | awk '{print $2}' | xargs -r kill -9
    sleep 1
    log "${RED}Script exited at $(date '+%Y-%m-%d %H:%M:%S') due to Ctrl+C or termination.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

pkill -f scripts/click_and_type.py 2>/dev/null

LAST_CYCLE_TIME=$(date +%s)
LOOP_COUNT=0

# SINGLE RUN FOR DEBUGGING
LOOP_COUNT=$((LOOP_COUNT+1))
log "${CYAN}[DEBUG] Starting loop iteration $LOOP_COUNT${NC}"

WAITING_TIME=$(jq -r '.waiting_time // 3' "$CONFIG_FILE" 2>/dev/null)
if ! [[ "$WAITING_TIME" =~ ^[0-9.]+$ ]]; then
    log "${RED}Invalid or missing waiting_time. Defaulting to 3 minutes.${NC}"
    WAITING_TIME=3
fi

log "${MAGENTA}==================== AUTOMATION RUN ===================="
log "${YELLOW}Coordinates and message found. Killing any prior automation instances...${NC}"
pkill -f scripts/click_and_type.py 2>/dev/null
sleep 1

log "${GREEN}Running automation script...${NC}"
log "${CYAN}[DEBUG] About to execute: python3 scripts/click_and_type_multi_linux.py${NC}"

# Run with explicit debugging
python3 scripts/click_and_type_multi_linux.py &
PYTHON_PID=$!

log "${CYAN}[DEBUG] Python process started with PID: $PYTHON_PID${NC}"

# Wait for up to 15 seconds for the Python script to complete
for i in {1..15}; do
    if kill -0 $PYTHON_PID 2>/dev/null; then
        log "${CYAN}[DEBUG] Python process still running after $i seconds${NC}"
        sleep 1
    else
        log "${CYAN}[DEBUG] Python process completed after $i seconds${NC}"
        break
    fi
    done

# Check if process is still running
if kill -0 $PYTHON_PID 2>/dev/null; then
    log "${RED}[DEBUG] Python process hung after 15 seconds, killing it${NC}"
    kill -9 $PYTHON_PID
    log "${RED}[ERROR] Python script hung and was killed${NC}"
else
    wait $PYTHON_PID
    PYTHON_EXIT_CODE=$?
    log "${CYAN}[DEBUG] Python script completed with exit code: $PYTHON_EXIT_CODE${NC}"
fi

log "${GREEN}Debug run completed${NC}"
