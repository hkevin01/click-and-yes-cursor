#!/bin/bash

# Robust automation runner with proper looping
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

log_with_time() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1"
}

cleanup() {
    log_with_time "[INFO] 🛑 Shutdown signal received"
    log_with_time "[INFO] Cleaning up..."
    pkill -f "click_and_type_multi_linux.py" 2>/dev/null || true
    log_with_time "[INFO] === AUTOMATION RUNNER TERMINATED ==="
    exit 0
}

trap cleanup SIGINT SIGTERM

log_with_time "=== AUTOMATION RUNNER STARTING ==="
log_with_time "Press Ctrl+C to stop gracefully"

# Use 15 second intervals
WAIT_TIME=15

LOOP_COUNT=0
while true; do
    LOOP_COUNT=$((LOOP_COUNT + 1))
    log_with_time "==================== RUN #$LOOP_COUNT ===================="
    # Validate config
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
    # Run automation
    if timeout 45 python3 scripts/click_and_type_multi_linux.py; then
        log_with_time "✓ Automation run #$LOOP_COUNT completed successfully"
    else
        log_with_time "⚠ Automation run #$LOOP_COUNT completed with issues"
    fi
    log_with_time "Waiting $WAIT_TIME seconds before next run... (Press Ctrl+C to exit)"
    # Interruptible sleep
    for ((i=0; i<WAIT_TIME; i++)); do
        sleep 1
    done
done
