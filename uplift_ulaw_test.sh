#!/bin/bash
docker exec aios-tts-router python3 -c "
import urllib.request, json, os
key = os.environ.get('UPLIFTAI_API_KEY', '')

# Test ULAW_8000_8 format
payload = {
    'voiceId': 'v_meklc281',
    'text': 'Assalam-o-Alaikum! Main Zara bol rahi hoon. Imperium Developers mein aap ki kya madad kar sakti hoon?',
    'outputFormat': 'ULAW_8000_8'
}
req = urllib.request.Request(
    'https://api.upliftai.org/v1/synthesis/text-to-speech',
    data=json.dumps(payload).encode(),
    headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
)
try:
    resp = urllib.request.urlopen(req)
    data = resp.read()
    print(f'ULAW_8000_8: Status={resp.status}, Size={len(data)} bytes, Type={resp.headers.get(\"Content-Type\")}')
    # ULAW is 8-bit, 8000Hz = 8000 bytes/sec
    duration = len(data) / 8000
    print(f'Duration: {duration:.2f}s at 8kHz')
except urllib.error.HTTPError as e:
    print(f'ULAW_8000_8 Error: {e.code}')
    print(e.read().decode()[:200])

# Compare with PCM_22050_16
payload2 = {**payload, 'outputFormat': 'PCM_22050_16'}
req2 = urllib.request.Request(
    'https://api.upliftai.org/v1/synthesis/text-to-speech',
    data=json.dumps(payload2).encode(),
    headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
)
try:
    resp2 = urllib.request.urlopen(req2)
    data2 = resp2.read()
    print(f'PCM_22050_16: Status={resp2.status}, Size={len(data2)} bytes')
    duration2 = len(data2) / 2 / 22050
    print(f'Duration: {duration2:.2f}s at 22kHz')
except urllib.error.HTTPError as e:
    print(f'PCM Error: {e.code}')
    print(e.read().decode()[:200])
"
