#!/bin/bash

# Robust automation runner with proper signal handling
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Global variables
AUTOMATION_PID=""
LOOP_ITERATION=0

# Cleanup function
cleanup() {
    local exit_code=$?
    echo ""
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] 🛑 Shutdown signal received"
    if [ ! -z "$AUTOMATION_PID" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] Terminating automation process $AUTOMATION_PID..."
        kill -TERM "$AUTOMATION_PID" 2>/dev/null || true
        wait "$AUTOMATION_PID" 2>/dev/null || true
    fi
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] Cleaning up any remaining automation processes..."
    pkill -f "click_and_type_multi_linux.py" 2>/dev/null || true
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] === AUTOMATION RUNNER TERMINATED ==="
    exit $exit_code
}

trap cleanup SIGINT SIGTERM

log_with_time() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1"
}

debug_log() {
    if [ "${DEBUG:-}" = "1" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') [DEBUG] $1"
    fi
}

check_dependencies() {
    local missing_deps=()
    for cmd in python3 jq wmctrl xdotool; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_deps+=("$cmd")
        fi
    done
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_with_time "[ERROR] Missing dependencies: ${missing_deps[*]}"
        log_with_time "[ERROR] Please install with: sudo apt install ${missing_deps[*]}"
        exit 1
    fi
}

load_config() {
    if [ ! -f "src/config.json" ]; then
        log_with_time "[ERROR] Configuration file not found: src/config.json"
        exit 1
    fi
    WAITING_TIME=$(jq -r '.waiting_time // 1.0' src/config.json)
    SLEEP_SECONDS=$(python3 -c "print(int($WAITING_TIME * 60))")
    debug_log "WAITING_TIME=$WAITING_TIME, SLEEP_SECONDS=$SLEEP_SECONDS"
}

run_automation() {
    log_with_time "==================== AUTOMATION RUN ===================="
    local has_windows=$(jq -e '.windows | length > 0' src/config.json 2>/dev/null)
    local has_message=$(jq -e '.message | length > 0' src/config.json 2>/dev/null)
    if [ "$has_windows" != "true" ] || [ "$has_message" != "true" ]; then
        log_with_time "Configuration incomplete. Skipping this run."
        return
    fi
    log_with_time "Configuration valid. Running automation..."
    pkill -f "click_and_type_multi_linux.py" 2>/dev/null || true
    sleep 0.5
    timeout 30 python3 scripts/click_and_type_multi_linux.py &
    AUTOMATION_PID=$!
    if wait "$AUTOMATION_PID"; then
        log_with_time "✓ Automation completed successfully"
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            log_with_time "[WARNING] Automation timed out after 30 seconds"
        else
            log_with_time "[ERROR] Automation failed with exit code $exit_code"
        fi
    fi
    AUTOMATION_PID=""
}

main() {
    log_with_time "=== ROBUST AUTOMATION RUNNER STARTING ==="
    log_with_time "Press Ctrl+C to stop gracefully"
    check_dependencies
    load_config
    while true; do
        LOOP_ITERATION=$((LOOP_ITERATION + 1))
        debug_log "Starting loop iteration $LOOP_ITERATION"
        load_config
        debug_log "Will sleep for $SLEEP_SECONDS seconds (waiting_time=$WAITING_TIME)"
        run_automation
        log_with_time "Waiting $WAITING_TIME minutes before next run... (Press Ctrl+C to exit)"
        debug_log "About to sleep for $SLEEP_SECONDS seconds."
        local start_time=$(date +%s)
        local elapsed=0
        while [ $elapsed -lt $SLEEP_SECONDS ]; do
            sleep 1
            elapsed=$((elapsed + 1))
            if [ $((elapsed % 10)) -eq 0 ]; then
                debug_log "Sleep progress: $elapsed/$SLEEP_SECONDS seconds"
            fi
        done
        local end_time=$(date +%s)
        local actual_elapsed=$((end_time - start_time))
        debug_log "Woke up from sleep, continuing loop."
        debug_log "Actual elapsed time this cycle: ${actual_elapsed}s"
        debug_log "End of loop iteration $LOOP_ITERATION"
    done
}

if [ "${1:-}" = "--debug" ]; then
    export DEBUG=1
    shift
fi

main "$@"
