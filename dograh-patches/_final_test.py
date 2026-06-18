import urllib.request, json

b = "http://10.0.0.100:8081"
h = {"Content-Type": "application/json"}

r = json.loads(urllib.request.urlopen(urllib.request.Request(b + "/api/sessions", data=b"{}", headers=h, method="POST"), timeout=30).read().decode())
sid = r["workflow_run_id"]
print("SID:", sid)

data = json.dumps({"text": "What is your address?"}).encode()
r2 = json.loads(urllib.request.urlopen(urllib.request.Request(b + "/api/sessions/" + str(sid) + "/messages", data=data, headers=h, method="POST"), timeout=120).read().decode())

for t in r2.get("session_data",{}).get("turns",[]):
    at = (t.get("assistant_message") or {}).get("text","")
    if at and ("123 High Street" in at or "123" in at):
        print("FOUND:", at[:200])
        break
else:
    for t in reversed(r2.get("session_data",{}).get("turns",[])):
        at = (t.get("assistant_message") or {}).get("text","")
        if at:
            print("LAST:", at[:200])
            break
