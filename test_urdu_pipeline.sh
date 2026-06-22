#!/bin/bash
# Test tts-router with known-good Urdu text
curl -s -X POST http://localhost:8030/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Assalam-o-Alaikum! Imperium Developers mein aapka khush amdeed. Main Zara bol rahi hoon.",
    "voice": "uplift",
    "response_format": "pcm"
  }' -o /tmp/test_urdu.pcm

BYTES=$(wc -c < /tmp/test_urdu.pcm)
SAMPLES=$((BYTES / 2))
DURATION=$(echo "scale=2; $SAMPLES / 8000" | bc)
echo "PCM: $BYTES bytes, $SAMPLES samples, ${DURATION}s @ 8000Hz"

# Check tts-router logs for this test
docker logs aios-tts-router --tail 5 2>&1
