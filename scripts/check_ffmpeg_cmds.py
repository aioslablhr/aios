#!/usr/bin/env python3
"""Check what ffmpeg commands Frigate generates."""
import json, subprocess

# Get config
r = subprocess.run(["curl", "-s", "http://10.0.0.100:5000/api/config"], capture_output=True, text=True, timeout=10)
cfg = json.loads(r.stdout)
entrance = cfg["cameras"]["entrance"]

# Check the ffmpeg commands generated
print("=== Camera ffmpeg cmds ===")
for cmd in entrance.get("ffmpeg_cmds", []):
    print(f"Roles: {cmd['roles']}")
    print(f"Cmd: {cmd['cmd']}")
    print()
