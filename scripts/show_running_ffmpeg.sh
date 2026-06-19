#!/bin/bash
# Show all ffmpeg processes with their full command lines
for pid in $(docker exec aios-frigate sh -c 'ls /proc/ | grep -E "^[0-9]+$"'); do
  cmd=$(docker exec aios-frigate sh -c "cat /proc/$pid/cmdline 2>/dev/null" | tr '\0' ' ')
  if echo "$cmd" | grep -q "ffmpeg"; then
    echo "=== PID $pid ==="
    echo "$cmd"
    echo ""
  fi
done
