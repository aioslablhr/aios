#!/usr/bin/env python3
"""Test camera auth from frigate container using Python requests."""
import subprocess, json

# Using requests library
script = '''
import requests
from requests.auth import HTTPDigestAuth

# Test 1: requests library with Digest auth
try:
    r = requests.get(
        "http://10.0.0.51/cgi-bin/snapshot.cgi",
        auth=HTTPDigestAuth("admin", "Lahore*999"),
        timeout=5
    )
    print(f"Test 1 (requests+digest): status={r.status_code}, len={len(r.content)}")
except Exception as e:
    print(f"Test 1 FAILED: {e}")

# Test 2: requests with explicit digest
try:
    r = requests.get(
        "http://10.0.0.51/cgi-bin/snapshot.cgi",
        auth=HTTPDigestAuth("admin", "Lahore*999"),
        timeout=5
    )
    print(f"Test 2 (explicit digest): status={r.status_code}, len={len(r.content)}")
except Exception as e:
    print(f"Test 2 FAILED: {e}")
'''

result = subprocess.run(
    ["docker", "exec", "aios-frigate", "python3", "-c", script],
    capture_output=True, text=True, timeout=10
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[-300:])
