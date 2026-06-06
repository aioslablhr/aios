#!/bin/bash
# Check whisper models available in Ollama
echo "=== Current Ollama models ==="
curl -s http://10.40.0.20:11434/api/tags | python3 -m json.tool | grep '"name"'

echo ""
echo "=== Pulling whisper-small ==="
curl -s -X POST http://10.40.0.20:11434/api/pull -H "Content-Type: application/json" -d '{"model":"whisper-small"}' &

# Wait for pull
PULL_PID=$!
echo "Pull started (PID: $PULL_PID), waiting up to 5 minutes..."
sleep 300 || true

echo ""
echo "=== Final model list ==="
curl -s http://10.40.0.20:11434/api/tags | python3 -m json.tool | grep '"name"'
