import urllib.request, json, os
key = os.environ.get('UPLIFTAI_API_KEY', '')

# Roman Urdu (what LLM generates)
roman = 'Assalam-o-Alaikum! Imperium Developers mein aapka khush amdeed. Main Zara bol rahi hoon.'

# Nastaliq Urdu (proper script)
nastaliq = 'السلام علیکم! امپیریم ڈویلپرز میں آپ کا خوش آمدید۔ میں زارا بول رہی ہوں۔'

for voice_id in ['v_meklc281', 'street-vendor']:
    for text_name, text in [('roman', roman), ('nastaliq', nastaliq)]:
        payload = {'voiceId': voice_id, 'text': text, 'outputFormat': 'ULAW_8000_8'}
        req = urllib.request.Request(
            'https://api.upliftai.org/v1/synthesis/text-to-speech',
            data=json.dumps(payload).encode(),
            headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}
        )
        try:
            resp = urllib.request.urlopen(req)
            data = resp.read()
            print(f'{voice_id} {text_name}: ULAW {len(data)} bytes, {len(data)/8000:.2f}s')
            # Save files for comparison
            fname = f'/tmp/{voice_id}_{text_name}.ulaw'
            open(fname, 'wb').write(data)
        except urllib.error.HTTPError as e:
            print(f'{voice_id} {text_name}: ERROR {e.code}')

print('\n=== File sizes for comparison ===')
import os as os2
for f in sorted(os2.listdir('/tmp')):
    if f.endswith('.ulaw'):
        sz = os2.path.getsize(f'/tmp/{f}')
        print(f'  {f}: {sz} bytes')
