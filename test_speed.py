import urllib.request, json, os
key = os.environ["UPLIFTAI_API_KEY"]
for spd in [1.0, 0.7, 0.5]:
    p = {"voiceId": "helpdesk-agent", "text": "Assalam-o-Alaikum! Main Zara bol rahi hoon.", "outputFormat": "ULAW_8000_8"}
    if spd != 1.0:
        p["speed"] = spd
    req = urllib.request.Request("https://api.upliftai.org/v1/synthesis/text-to-speech", data=json.dumps(p).encode(), headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    r = urllib.request.urlopen(req)
    d = r.read()
    print(f"speed={spd}: {len(d)} bytes = {len(d)/8000:.2f}s")
