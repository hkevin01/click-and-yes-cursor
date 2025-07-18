#!/bin/bash
for i in {1..5}; do
    echo "[LOOP TEST] $(date '+%Y-%m-%d %H:%M:%S') Iteration $i"
    sleep 5
done
