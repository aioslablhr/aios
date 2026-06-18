import urllib.request, json

h = {"X-API-Key":"dgr_JxFoGXkzncAlJM2aUhPhFOZ_GCQKgBHpajfgH15V0Bc","Content-Type":"application/json"}
b = "http://10.50.0.30:8000"

# Create session with address in initial_context
body = json.dumps({"initial_context": {"office_address": "123 High Street, London, E1 1AA"}}).encode()
r = json.loads(urllib.request.urlopen(urllib.request.Request(b + "/api/v1/workflow/1/text-chat/sessions", data=body, headers=h, method="POST"), timeout=30).read().decode())
sid = r["workflow_run_id"]
print("SID:", sid)

# Ask for address
data = json.dumps({"text": "What is your office address?"}).encode()
r2 = json.loads(urllib.request.urlopen(urllib.request.Request(b + "/api/v1/workflow/1/text-chat/sessions/" + str(sid) + "/messages", data=data, headers=h, method="POST"), timeout=120).read().decode())

for t in reversed(r2.get("session_data",{}).get("turns",[])):
    at = (t.get("assistant_message") or {}).get("text","")
    if at:
        print("EMMA:", at[:300])
        print("HAS ADDRESS:", "123 High Street" in at)
        break
