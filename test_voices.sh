#!/bin/bash
docker exec aios-tts-router python3 << 'PYEOF'
import urllib.request, json, os
key = os.environ.get('UPLIFTAI_API_KEY', '')

for voice_id in ['v_meklc281', 'street-vendor']:
    for fmt in ['MP3_22050_128', 'ULAW_8000_8']:
        payload = {
            'voiceId': voice_id,
            'text': 'Assalam-o-Alaikum! Main Zara bol rahi hoon. Imperium Developers mein aap ki kya madad kar sakti hoon?',
            'outputFormat': fmt
        }
        req = urllib.request.Request(
            'https://api.upliftai.org/v1/synthesis/text-to-speech',
            data=json.dumps(payload).encode(),
            headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
        )
        try:
            resp = urllib.request.urlopen(req)
            data = resp.read()
            print(f'{voice_id} {fmt}: {resp.status}, {len(data)} bytes')
        except urllib.error.HTTPError as e:
            print(f'{voice_id} {fmt}: ERROR {e.code}: {e.read().decode()[:100]}')
PYEOF
