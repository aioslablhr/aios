#!/bin/bash
echo "=== Dograh -> tts-router connectivity ==="
docker exec aios-dograh-api python3 -c "
import urllib.request
try:
    resp = urllib.request.urlopen('http://aios-tts-router:8030/health', timeout=5)
    print(f'tts-router reachable: {resp.status}')
    print(resp.read().decode())
except Exception as e:
    print(f'Cannot reach tts-router: {e}')
"

echo ""
echo "=== Dograh TTS config ==="
docker exec -e PGPASSWORD=aios_secret_2026 aios-postgres psql -h localhost -U aios -d dograh -t -A -c "
select workflow_configurations::json->'model_overrides'->'tts' 
from workflow_definitions where id=4;
"

echo ""
echo "=== Dograh recent logs (TTS related) ==="
docker logs aios-dograh-api --tail 100 2>&1 | grep -iE "tts|uplift|audio|speech|openai" | tail -10
