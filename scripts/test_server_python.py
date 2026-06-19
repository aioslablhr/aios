#!/usr/bin/env python3
"""Test camera auth from server using Python requests."""
import requests
from requests.auth import HTTPDigestAuth

r = requests.get(
    "http://10.0.0.51/cgi-bin/snapshot.cgi",
    auth=HTTPDigestAuth("admin", "Lahore*999"),
    timeout=5,
    headers={"User-Agent": "Mozilla/5.0"}
)
print(f"Status: {r.status_code}")
print(f"Headers: {dict(r.headers)}")
print(f"Content: {r.content[:100]}")
