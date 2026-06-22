import urllib.request, json, os
key = os.getenv('UPLIFTAI_API_KEY', '')

# Test what happens with unknown voice ID
for vid in ['helpdesk-agent', 'v_meklc281', 'nonexistent-voice']:
    payload = {
        'voiceId': vid,
        'text': 'Assalam-o-Alaikum! Main Zara bol rahi hoon.',
        'outputFormat': 'ULAW_8000_8'
    }
    req = urllib.request.Request(
        'https://api.upliftai.org/v1/synthesis/text-to-speech',
        data=json.dumps(payload).encode(),
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}
    )
    try:
        resp = urllib.request.urlopen(req)
        data = resp.read()
        print(f'{vid}: OK {len(data)} bytes')
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:100]
        print(f'{vid}: ERROR {e.code}: {body}')
