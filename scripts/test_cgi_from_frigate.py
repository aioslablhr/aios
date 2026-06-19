#!/usr/bin/env python3
"""Test Snapshot CGI from within Frigate container."""
import subprocess

# Test snapshot from within frigate container
cmd = [
    "docker", "exec", "aios-frigate",
    "curl", "-s", "--digest",
    "-u", "admin:Lahore*999",
    "http://10.0.0.51/cgi-bin/snapshot.cgi",
    "-o", "/tmp/snap_test.jpg",
    "-w", "%{http_code}"
]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
print(f"HTTP code: {result.stdout}")

# Check file size
cmd2 = ["docker", "exec", "aios-frigate", "ls", "-la", "/tmp/snap_test.jpg"]
result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=5)
print(f"File info: {result2.stdout}")
