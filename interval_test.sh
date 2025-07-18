#!/bin/bash
# interval_test.sh: Log timestamps every 10 seconds for 1 minute to verify interval timing
for i in {1..6}; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') Interval test tick $i" >> logs/interval_test.log
    sleep 10
done
