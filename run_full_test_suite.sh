#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/test_suite.log"
mkdir -p "$LOG_DIR"
echo "[TEST SUITE] Started at $(date)" > "$LOG_FILE"

# Run Python tests with pytest if available
if command -v pytest &> /dev/null; then
    echo "[TEST SUITE] Running pytest..." | tee -a "$LOG_FILE"
    pytest --maxfail=5 --disable-warnings | tee -a "$LOG_FILE"
else
    echo "[TEST SUITE] pytest not found, skipping." | tee -a "$LOG_FILE"
fi

# Run Python unittest discovery
echo "[TEST SUITE] Running unittest discovery..." | tee -a "$LOG_FILE"
python3 -m unittest discover | tee -a "$LOG_FILE"

# Run any test_*.sh scripts
for f in "$SCRIPT_DIR"/test_*.sh; do
    if [ -f "$f" ]; then
        echo "[TEST SUITE] Running $f..." | tee -a "$LOG_FILE"
        bash "$f" | tee -a "$LOG_FILE"
    fi
done

echo "[TEST SUITE] Finished at $(date)" | tee -a "$LOG_FILE"
echo "[TEST SUITE] See $LOG_FILE for full output."
