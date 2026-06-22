#!/bin/bash
echo "=== Check for more 'Failed to write audio frame' ==="
docker logs aios-dograh-api --tail 500 2>&1 | grep -c "Failed to write audio frame"

echo ""
echo "=== Full context around the error ==="
docker logs aios-dograh-api --tail 500 2>&1 | grep -B5 -A5 "Failed to write audio frame" | tail -50

echo ""
echo "=== ARI transport errors ==="
docker logs aios-dograh-api --tail 500 2>&1 | grep -iE "ari|transport|channel|bridge|codec|format|slin|ulaw|alaw" | tail -20

echo ""
echo "=== check audio format in Asterisk ==="
docker exec aios-asterisk asterisk -rx "core show channel 105" 2>/dev/null | head -20
