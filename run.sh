#!/bin/bash

# Robust automation runner with proper looping
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

log_with_time() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1"
}

cleanup() {
    log_with_time "[INFO] 🛑 Shutdown signal received"
    log_with_time "[INFO] Cleaning up any remaining automation processes..."
    pkill -f "click_and_type_multi_linux.py" 2>/dev/null || true
    log_with_time "[INFO] === AUTOMATION RUNNER TERMINATED ==="
    exit 0
}

trap cleanup SIGINT SIGTERM

log_with_time "=== ROBUST AUTOMATION RUNNER STARTING ==="
log_with_time "Press Ctrl+C to stop gracefully"

WAIT_TIME=$(python3 -c "
import json
try:
    with open('src/config.json') as f:
        config = json.load(f)
    wait_minutes = config.get('waiting_time', 0.5)
    print(int(wait_minutes * 60))
except:
    print(30)
" 2>/dev/null || echo "30")

LOOP_COUNT=0
while true; do
    LOOP_COUNT=$((LOOP_COUNT + 1))
    log_with_time "==================== AUTOMATION RUN #$LOOP_COUNT ===================="
    if ! python3 -c "
import json
with open('src/config.json') as f:
    config = json.load(f)
assert config.get('windows'), 'No windows configured'
assert config.get('message'), 'No messages configured'
print('Configuration valid. Running automation...')
"; then
        log_with_time "❌ Configuration invalid. Skipping this run."
        sleep 10
        continue
    fi
    if timeout 45 python3 scripts/click_and_type_multi_linux.py; then
        log_with_time "✓ Automation run #$LOOP_COUNT completed successfully"
    else
        log_with_time "⚠ Automation run #$LOOP_COUNT completed with issues"
    fi
    log_with_time "Waiting $WAIT_TIME seconds before next run... (Press Ctrl+C to exit)"
    for ((i=0; i<WAIT_TIME; i++)); do
        sleep 1
        if ! kill -0 $$ 2>/dev/null; then
            exit 0
        fi
    done
done
