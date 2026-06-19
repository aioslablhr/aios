#!/bin/bash
# Test from server host directly using python3
echo "=== Test HTTP from server host ==="
python3 -c "
import urllib.request, base64

# Test 1: Basic auth
req = urllib.request.Request('http://10.0.0.51/cgi-bin/snapshot.cgi')
creds = base64.b64encode(b'admin:Lahore*999').decode()
req.add_header('Authorization', f'Basic {creds}')
try:
    resp = urllib.open(req)
    print(f'Basic auth: {resp.status}, len={len(resp.read())}')
except Exception as e:
    print(f'Basic auth failed: {e}')

# Test 2: Try with different user-agent
req2 = urllib.request.Request('http://10.0.0.51/cgi-bin/snapshot.cgi')
req2.add_header('User-Agent', 'Mozilla/5.0')
creds = base64.b64encode(b'admin:Lahore*999').decode()
req2.add_header('Authorization', f'Basic {creds}')
try:
    resp2 = urllib.open(req2)
    print(f'Basic + Mozilla UA: {resp2.status}, len={len(resp2.read())}')
except Exception as e:
    print(f'Basic + Mozilla UA failed: {e}')
" 2>&1
