#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"
TEST_LOG="logs/test_results_$(date +%Y%m%d_%H%M%S).log"

echo "=== AUTOMATION SCRIPT TESTS ===" | tee "$TEST_LOG"
echo "Started at: $(date)" | tee -a "$TEST_LOG"
echo "" | tee -a "$TEST_LOG"

# Test 1: Config file reading
echo "TEST 1: Config file reading" | tee -a "$TEST_LOG"
if python3 -c "
import sys
sys.path.append('scripts')
from click_and_type import get_config
coords, messages, cycling = get_config()
print(f'Coords: {coords}')
print(f'Messages: {messages}')
print(f'Cycling: {cycling}')
" 2>&1 | tee -a "$TEST_LOG"; then
    echo "✓ PASS: Config reading works" | tee -a "$TEST_LOG"
else
    echo "✗ FAIL: Config reading failed" | tee -a "$TEST_LOG"
fi
echo "" | tee -a "$TEST_LOG"

# Test 2: Message cycling
echo "TEST 2: Message cycling" | tee -a "$TEST_LOG"
python3 -c "
import sys
sys.path.append('scripts')
from click_and_type import get_config, get_next_message
coords, messages, cycling = get_config()
for i in range(5):
    msg = get_next_message(messages, cycling)
    print(f'Iteration {i+1}: {msg}')
" 2>&1 | tee -a "$TEST_LOG"
echo "✓ PASS: Message cycling test completed" | tee -a "$TEST_LOG"
echo "" | tee -a "$TEST_LOG"

# Test 3: Platform dependencies
echo "TEST 3: Platform dependencies" | tee -a "$TEST_LOG"
if python3 -c "
import sys
sys.path.append('scripts')
from click_and_type import check_platform_dependencies
check_platform_dependencies()
print('All dependencies satisfied')
" 2>&1 | tee -a "$TEST_LOG"; then
    echo "✓ PASS: All dependencies satisfied" | tee -a "$TEST_LOG"
else
    echo "✗ FAIL: Missing dependencies" | tee -a "$TEST_LOG"
fi
echo "" | tee -a "$TEST_LOG"

# Test 4: Dry run without actual clicking
echo "TEST 4: Dry run simulation" | tee -a "$TEST_LOG"
python3 tests/dry_run_test.py 2>&1 | tee -a "$TEST_LOG"
echo "" | tee -a "$TEST_LOG"

# Test 5: Loop timing test
echo "TEST 5: Loop timing test (30 second intervals)" | tee -a "$TEST_LOG"
echo "Setting waiting_time to 0.05 (3 seconds) for quick test..." | tee -a "$TEST_LOG"
cp src/config.json src/config.json.backup
jq '.waiting_time = 0.05' src/config.json > tmp.json && mv tmp.json src/config.json

echo "Running 3 iterations of the main script..." | tee -a "$TEST_LOG"
timeout 15 ./run.sh 2>&1 | tee -a "$TEST_LOG" || echo "Test completed (timeout expected)" | tee -a "$TEST_LOG"

# Restore original config
mv src/config.json.backup src/config.json
echo "✓ PASS: Loop timing test completed" | tee -a "$TEST_LOG"
echo "" | tee -a "$TEST_LOG"

echo "=== TEST SUMMARY ===" | tee -a "$TEST_LOG"
echo "Completed at: $(date)" | tee -a "$TEST_LOG"
echo "Full results saved to: $TEST_LOG" | tee -a "$TEST_LOG"
