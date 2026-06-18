import urllib.request, json

h = {"Content-Type": "application/json"}
b = "http://10.0.0.100:8081"

r = json.loads(urllib.request.urlopen(urllib.request.Request(b + "/api/sessions", data=b"{}", headers=h, method="POST"), timeout=30).read().decode())
sid = r["workflow_run_id"]
print("Session:", sid)

data = json.dumps({"text": "What is your address?"}).encode()
r2 = json.loads(urllib.request.urlopen(urllib.request.Request(b + "/api/sessions/" + str(sid) + "/messages", data=data, headers=h, method="POST"), timeout=120).read().decode())

for t in reversed(r2.get("session_data",{}).get("turns",[])):
    at = (t.get("assistant_message") or {}).get("text","")
    if at:
        print("EMMA:", at[:300])
        print("OK:", "123 High Street" in at)
        break
