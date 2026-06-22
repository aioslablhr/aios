#!/bin/bash
echo "=== Logs ==="
docker logs aios-tts-router --tail 3

echo "=== Test ==="
docker exec aios-tts-router python3 -c '
import urllib.request, json
req = urllib.request.Request(
    "http://localhost:8030/v1/audio/speech",
    data=json.dumps({"model":"tts-1","input":"\u0627\u0644\u0633\u0644\u0627\u0645 \u0639\u0644\u06cc\u06a9\u0645","voice":"uplift","response_format":"pcm"}).encode(),
    headers={"Content-Type":"application/json"}
)
resp = urllib.request.urlopen(req)
d = resp.read()
print(f"OK {len(d)} bytes, {resp.headers.get(\"Content-Type\")}")
'

echo "=== Recent log ==="
docker logs aios-tts-router --tail 4
