#!/bin/bash
docker exec aios-tts-router python3 -c "
import urllib.request, json, os
key = os.environ.get('UPLIFTAI_API_KEY', '')
payload = {
    'voiceId': 'v_meklc281',
    'text': 'Assalam-o-Alaikum! Main Zara bol rahi hoon. Imperium Developers mein aap ki kya madad kar sakti hoon?',
    'outputFormat': 'MP3_22050_128'
}
print(f'Using key: {key[:20]}...')
req = urllib.request.Request(
    'https://api.upliftai.org/v1/synthesis/text-to-speech',
    data=json.dumps(payload).encode(),
    headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
)
try:
    resp = urllib.request.urlopen(req)
    data = resp.read()
    print(f'Status: {resp.status}')
    print(f'Size: {len(data)} bytes')
    print(f'Type: {resp.headers.get(\"Content-Type\", \"unknown\")}')
except urllib.error.HTTPError as e:
    print(f'HTTP Error: {e.code}')
    print(f'Response: {e.read().decode()[:200]}')
"
