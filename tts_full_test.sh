#!/bin/bash
# Test full tts-router pipeline from within container
docker exec aios-tts-router python3 -c "
import urllib.request, json
payload = {
    'model': 'tts-1',
    'input': 'Assalam-o-Alaikum! Main Zara bol rahi hoon. Imperium Developers mein aap ki kya madad kar sakti hoon?',
    'voice': 'uplift',
    'response_format': 'pcm'
}
req = urllib.request.Request(
    'http://localhost:8030/v1/audio/speech',
    data=json.dumps(payload).encode(),
    headers={'Content-Type': 'application/json'}
)
resp = urllib.request.urlopen(req)
data = resp.read()
content_type = resp.headers.get('Content-Type', 'unknown')
print(f'Status: {resp.status}')
print(f'Content-Type: {content_type}')
print(f'Size: {len(data)} bytes')
samples = len(data) // 2
print(f'Samples: {samples}')
print(f'Duration at 8kHz: {samples/8000:.2f}s')
print(f'Duration at 22kHz: {samples/22050:.2f}s')
print(f'Duration at 24kHz: {samples/24000:.2f}s')

# Also test same text via tts-router but MP3 format (no resampling)
payload2 = {**payload, 'response_format': 'mp3'}
req2 = urllib.request.Request(
    'http://localhost:8030/v1/audio/speech',
    data=json.dumps(payload2).encode(),
    headers={'Content-Type': 'application/json'}
)
resp2 = urllib.request.urlopen(req2)
data2 = resp2.read()
print(f'\nMP3 path: {resp2.status}, {len(data2)} bytes, {resp2.headers.get(\"Content-Type\", \"unknown\")}')
"
