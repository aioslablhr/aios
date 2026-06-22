import urllib.request, json, os
key = os.getenv('UPLIFTAI_API_KEY', '')

# Test Nastaliq Urdu text through the tts-router
req = urllib.request.Request(
    'http://localhost:8030/v1/audio/speech',
    data=json.dumps({
        'model': 'tts-1',
        'input': 'ہاں جی، بلکل۔ Sixty6 گلبرگ میں residential اور commercial دونوں available ہیں۔',
        'voice': 'uplift',
        'response_format': 'pcm'
    }).encode(),
    headers={'Content-Type': 'application/json'}
)
resp = urllib.request.urlopen(req)
data = resp.read()
print(f'Nastaliq thru pipeline: {resp.status}, {len(data)} bytes')
print(f'Content-Type: {resp.headers.get("Content-Type")}')
