import urllib.request, json, os, time
from datetime import datetime

TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJzb2NpYWxiZWVzYWlvc0BnbWFpbC5jb20iLCJleHAiOjE3ODQzMDI1MDksImlhdCI6MTc4MTcxMDUwOX0.yiXmH0FiIiKC3KvrEjBq_RDwlTVhKYHc1u3_-uuCsGU'
API_BASE = 'http://10.50.0.30:8000/api/v1'

CW_URL = 'http://10.70.0.50:3000/api/v1/accounts/1'
CW_TOKEN = 'S25Q5AkyFCGwUrXUzzn8SCYw'
INBOX_IDENTIFIER = '8xXig1ed5a9Ps4hQVjuMsrSL'

STATE_FILE = '/tmp/cw_last_run.txt'

def dograh_api(method, path, data=None):
    url = API_BASE + path
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        if resp.status == 204:
            return None, None
        return resp.status, json.loads(resp.read().decode())
    except urllib.request.HTTPError as e:
        return e.code, e.read().decode()[:300]

def cw_api(method, path, data=None):
    url = CW_URL + path
    headers = {'Content-Type': 'application/json', 'api_access_token': CW_TOKEN}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read())
    except urllib.request.HTTPError as e:
        return e.code, e.read().decode()[:200]

# Read last processed run ID
last_run = 0
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        last_run = int(f.read().strip())

print(f"Last processed run: {last_run}")

# Get workflow runs
status, data = dograh_api('GET', '/workflow/1/runs')
if status != 200:
    print(f"Error fetching runs: {data}")
    exit()

runs = data.get('runs', []) if isinstance(data, dict) else []
print(f"Found {len(runs)} total runs")

# Process new runs
new_runs = [r for r in runs if r.get('id', 0) > last_run]
new_runs.sort(key=lambda x: x.get('id', 0))

for run in new_runs:
    run_id = run.get('id')
    created = run.get('created_at', '')
    print(f"\n=== Processing run {run_id} ({created}) ===")
    
    # Get full run details with transcript
    status, detail = dograh_api('GET', f'/workflow/1/runs/{run_id}')
    if status != 200:
        print(f"  Error fetching details: {detail}")
        continue
    
    transcript_url = detail.get('transcript_public_url') or detail.get('transcript_url', '')
    recording_url = detail.get('recording_public_url') or detail.get('recording_url', '')
    
    # Get transcript content
    transcript = ""
    if transcript_url:
        try:
            req = urllib.request.Request(transcript_url)
            resp = urllib.request.urlopen(req)
            transcript = resp.read().decode('utf-8', errors='replace')
        except:
            pass
    
    # Get gathered context
    gathered = detail.get('gathered_context', {})
    call_id = gathered.get('call_id', f'run-{run_id}')
    disposition = detail.get('disposition', 'unknown')
    duration = run.get('call_duration_seconds', 0) or gathered.get('call_duration_seconds', 0)
    
    print(f"  Disposition: {disposition}, Duration: {duration}s")
    
    if not transcript:
        # Try public URL
        try:
            req = urllib.request.Request(transcript_url)
            resp = urllib.request.urlopen(req)
            transcript = resp.read().decode('utf-8', errors='replace')
        except:
            pass
    
    if not transcript:
        # Extract from logs
        log_events = detail.get('logs', {}).get('realtime_feedback_events', [])
        transcript_parts = []
        for event in log_events:
            etype = event.get('type', '')
            payload = event.get('payload', {})
            if etype == 'rtf-bot-text':
                transcript_parts.append(f"Emma: {payload.get('text', '')}")
            elif etype == 'rtf-user-transcription':
                transcript_parts.append(f"Caller: {payload.get('text', '')}")
        if transcript_parts:
            transcript = '\n'.join(transcript_parts)
    
    print(f"  Transcript ({len(transcript)} chars): {transcript[:100]}...")
    
    if not transcript:
        print(f"  No transcript data, skipping")
        last_run = max(last_run, run_id)
        continue
    
    # Create contact in Chatwoot
    contact_name = f"Call {run_id}"
    status, cw_resp = cw_api('POST', '/contacts', {
        'inbox_id': 1,
        'name': contact_name,
        'phone_number': f"+4412345678{run_id:02d}",
        'additional_attributes': {
            'call_id': call_id,
            'duration': duration,
            'disposition': disposition
        }
    })
    
    if status != 200:
        print(f"  Contact error ({status}): {cw_resp}")
        last_run = max(last_run, run_id)
        continue
    
    source_id = cw_resp.get('payload', {}).get('contact_inbox', {}).get('source_id', '')
    print(f"  Contact created, source_id: {source_id}")
    
    if not source_id:
        last_run = max(last_run, run_id)
        continue
    
    # Create conversation
    pub_url = f'http://10.70.0.50:3000/public/api/v1/inboxes/{INBOX_IDENTIFIER}/contacts/{source_id}/conversations'
    pub_req = urllib.request.Request(pub_url, data=b'{}',
        headers={'Content-Type': 'application/json'}, method='POST')
    try:
        pub_resp = urllib.request.urlopen(pub_req)
        conv = json.loads(pub_resp.read())
        conv_id = conv.get('id')
        print(f"  Conversation: {conv_id}")
        
        # Add transcript message
        msg_content = f"📞 Call #{run_id}\n"
        msg_content += f"Duration: {duration}s | Disposition: {disposition}\n\n"
        msg_content += f"Transcript:\n{transcript}"
        
        msg_url = f'{CW_URL}/conversations/{conv_id}/messages'
        msg_req = urllib.request.Request(msg_url,
            data=json.dumps({
                'content': msg_content,
                'message_type': 'incoming'
            }).encode(),
            headers={'Content-Type': 'application/json', 'api_access_token': CW_TOKEN},
            method='POST')
        msg_resp = urllib.request.urlopen(msg_req)
        print(f"  Message added: {msg_resp.status}")
        
    except urllib.request.HTTPError as e:
        print(f"  Conversation error: {e.code} {e.read().decode()[:200]}")
    
    last_run = run_id
    with open(STATE_FILE, 'w') as f:
        f.write(str(last_run))

print(f"\nDone. Last processed: {last_run}")
