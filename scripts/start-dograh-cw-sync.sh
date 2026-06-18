#!/bin/bash
# Auto-start for Dograh->Chatwoot sync
# Waits for Docker+Postgres, then launches in screen

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Wait for Docker and postgres to be ready
for i in $(seq 1 30); do
    docker ps 2>&1 | grep -q aios-postgres
    if [ $? -eq 0 ]; then
        break
    fi
    sleep 5
done

# Wait for postgres to accept connections
for i in $(seq 1 12); do
    docker exec aios-postgres psql -U aios -d dograh -c 'SELECT 1' 2>&1 | grep -q '1 row'
    if [ $? -eq 0 ]; then
        break
    fi
    sleep 5
done

# Kill existing screen session if any
screen -ls 2>/dev/null | grep -q cw_sync && screen -S cw_sync -X quit 2>/dev/null
sleep 1

# Launch in screen
screen -dmS cw_sync python3 /aios/scripts/dograh_cw_sync.py
echo "[cw_sync] started at $(date -u -Iseconds)"
