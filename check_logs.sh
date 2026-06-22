#!/bin/bash
PGPASSWORD=aios_secret_2026
echo "=== Tables ==="
docker exec -e PGPASSWORD=$PGPASSWORD aios-postgres psql -h localhost -U aios -d dograh -c "\dt" 2>/dev/null
echo ""
echo "=== Workflow runs ==="
docker exec -e PGPASSWORD=$PGPASSWORD aios-postgres psql -h localhost -U aios -d dograh -c "select count(*) from workflow_runs;" 2>/dev/null
echo ""
echo "=== TTS-Router logs ==="
docker logs aios-tts-router --tail 20 2>&1
echo ""
echo "=== Dograh recent logs ==="
docker logs aios-dograh-api --tail 20 2>&1 | grep -i -E "tts|uplift|error|warn|audio" | tail -10
