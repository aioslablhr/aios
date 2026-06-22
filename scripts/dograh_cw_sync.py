#!/usr/bin/env python3
"""
Dograh -> Chatwoot Sync Service
Polls PostgreSQL directly for completed workflow runs,
builds structured per-turn transcripts, pushes to Chatwoot as proper conversations.
Skips runs with <2 turns (no real conversation).
"""

import subprocess, json, urllib.request, os, time, sys
from datetime import datetime, timezone

DOGRAH_DB_HOST = os.environ.get('DOGRAH_DB_HOST', '10.30.0.10')
DOGRAH_DB_NAME = os.environ.get('DOGRAH_DB_NAME', 'dograh')
DOGRAH_DB_USER = os.environ.get('DOGRAH_DB_USER', 'aios')
DOGRAH_DB_PASS = os.environ.get('DOGRAH_DB_PASS', 'aios_secret_2026')
CW_URL = os.environ.get('CW_URL', 'http://10.70.0.50:3000/api/v1/accounts/1')
CW_TOKEN = os.environ.get('CW_TOKEN', 'S25Q5AkyFCGwUrXUzzn8SCYw')
INBOX_ID = int(os.environ.get('CW_INBOX_ID', '1'))
INBOX_IDENTIFIER = os.environ.get('CW_INBOX_IDENTIFIER', '8xXig1ed5a9Ps4hQVjuMsrSL')
STATE_FILE = os.environ.get('STATE_FILE', '/tmp/cw_sync_state.json')
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', '15'))

WORKFLOW_NAMES = {1: 'English', 5: 'Urdu'}


def log(msg):
    print('[%s] %s' % (datetime.now(timezone.utc).isoformat(), msg), flush=True)


def psql(query):
    cmd = ['docker', 'exec', 'aios-postgres', 'psql', '-U', DOGRAH_DB_USER, '-d', DOGRAH_DB_NAME, '-t', '-A', '-F', '|', '-c', query]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return r.stdout.strip()


def cw_api(method, path, data=None):
    url = CW_URL + path
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers={
        'Content-Type': 'application/json', 'api_access_token': CW_TOKEN
    }, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read()) if resp.status != 204 else None
    except urllib.request.HTTPError as e:
        err = e.read().decode()[:200] if e.fp else ''
        log('CW error %s %s: %d %s' % (method, path, e.code, err))
        return None


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f: return json.load(f)
    return {'synced_runs': [], 'backfilled': False}


def save_state(state):
    with open(STATE_FILE, 'w') as f: json.dump(state, f)


def parse_transcript(logs_json):
    if not isinstance(logs_json, dict): return []
    events = logs_json.get('realtime_feedback_events', [])
    turns = []
    for ev in events:
        etype, payload = ev.get('type', ''), ev.get('payload', {})
        text = payload.get('text', '').strip()
        if not text: continue
        if etype == 'rtf-bot-text':
            turns.append({'speaker': 'Emma', 'text': text})
        elif etype == 'rtf-user-transcription':
            turns.append({'speaker': 'Caller', 'text': text})
    return turns


def sync_run(run):
    rid, wfid = run['id'], run['workflow_id']
    wfname = WORKFLOW_NAMES.get(wfid, 'WF%d' % wfid)
    initial, gathered, logs_data = run.get('initial_context', {}), run.get('gathered_context', {}), run.get('logs', {})
    caller = initial.get('caller_number', 'unknown')
    called = initial.get('called_number', 'unknown')
    disposition = gathered.get('mapped_call_disposition') or gathered.get('call_disposition', 'unknown')
    call_id = gathered.get('call_id', 'run-%d' % rid)
    turns = parse_transcript(logs_data)
    if len(turns) < 2:
        log('  Run %d: skipped (only %d turns)' % (rid, len(turns)))
        return False

    log('  Run %d: %s | %s->%s | %s | %d turns' % (rid, wfname, caller, called, disposition, len(turns)))
    cname = 'Run %d: %s' % (rid, call_id)
    digits = ''.join(c for c in caller if c.isdigit())
    if not digits: digits = '0000000000'
    phone = '+' + digits
    if len(digits) <= 5: phone += '%05d' % rid

    contact = cw_api('POST', '/contacts', {
        'inbox_id': INBOX_ID, 'name': cname, 'phone_number': phone,
        'additional_attributes': {'call_id': call_id, 'workflow': wfname, 'workflow_id': wfid, 'disposition': disposition, 'called_number': called}
    })
    if not contact: return False
    source_id = (contact.get('payload', {}).get('contact_inbox', {}).get('source_id', ''))
    if not source_id: return False

    base = CW_URL.split('/api/v1/')[0]
    try:
        req = urllib.request.Request('%s/public/api/v1/inboxes/%s/contacts/%s/conversations' % (base, INBOX_IDENTIFIER, source_id), data=b'{}', headers={'Content-Type': 'application/json'}, method='POST')
        conv = json.loads(urllib.request.urlopen(req, timeout=15).read())
        conv_id = conv.get('id')
    except Exception as e:
        log('  Run %d: conv failed: %s' % (rid, e))
        return False

    log('  Run %d: conversation #%d' % (rid, conv_id))
    cw_api('POST', '/conversations/%d/messages' % conv_id, {
        'content': 'Call #%d - %s | %s -> %s | %s' % (rid, wfname, caller, called, disposition),
        'message_type': 'incoming'
    })
    for t in turns:
        cw_api('POST', '/conversations/%d/messages' % conv_id, {
            'content': '%s: %s' % (t['speaker'], t['text']), 'message_type': 'incoming'
        })
    cw_api('POST', '/conversations/%d/toggle_status' % conv_id, {'status': 'resolved'})
    log('  Run %d: done, resolved' % rid)
    return True


def fetch_new(state):
    synced = set(state.get('synced_runs', []))
    q = "SELECT id, workflow_id, state, initial_context::text, gathered_context::text, logs::text FROM workflow_runs WHERE state = 'completed'"
    if state.get('backfilled'):
        mx = max(synced) if synced else 0
        q += ' AND id > %d' % mx
    q += ' ORDER BY id'

    rows = psql(q)
    if not rows: return []
    runs = []
    for line in rows.split('\n'):
        line = line.strip()
        if not line or '|' not in line: continue
        parts = line.split('|')
        if len(parts) < 6: continue
        try:
            rid = int(parts[0])
            if rid in synced: continue
            runs.append({'id': rid, 'workflow_id': int(parts[1]), 'state': parts[2],
                         'initial_context': json.loads(parts[3]) if parts[3] else {},
                         'gathered_context': json.loads(parts[4]) if parts[4] else {},
                         'logs': json.loads(parts[5]) if parts[5] else {}})
        except: continue
    return runs


def main():
    log('Dograh->CW Sync starting (poll=%ds)' % POLL_INTERVAL)
    state = load_state()
    log('Already synced: %d runs' % len(state.get('synced_runs', [])))

    while True:
        try:
            runs = fetch_new(state)
            if not runs and not state.get('backfilled'):
                log('Backfill: no completed runs found')
                state['backfilled'] = True
                save_state(state)
            for run in runs:
                ok = sync_run(run)
                if ok:
                    state.setdefault('synced_runs', []).append(run['id'])
                    save_state(state)
                time.sleep(1)
            if not state.get('backfilled') and runs:
                state['backfilled'] = True
                save_state(state)
                log('Backfill complete: %d runs synced' % len(state['synced_runs']))
        except Exception as e:
            log('Loop error: %s' % e)
        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    main()
