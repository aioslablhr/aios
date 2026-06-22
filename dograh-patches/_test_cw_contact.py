import urllib.request, json

url = "http://10.70.0.50:3000/api/v1/accounts/1/contacts"
data = json.dumps({"inbox_id": 1, "name": "Test", "phone_number": "+44123456700122"}).encode()
req = urllib.request.Request(url, data=data, headers={
    "Content-Type": "application/json",
    "api_access_token": "S25Q5AkyFCGwUrXUzzn8SCYw"
}, method="POST")

try:
    r = urllib.request.urlopen(req, timeout=15)
    print("OK", r.status)
    resp = json.loads(r.read().decode())
    print("Contact ID:", resp.get("payload", {}).get("contact", {}).get("id"))
except Exception as e:
    print("FAIL", str(e))
