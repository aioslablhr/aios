#!/usr/bin/env python3
"""Check current Frigate ffmpeg cmds."""
import json, urllib.request, sys

r = urllib.request.urlopen("http://10.0.0.100:5000/api/config")
cfg = json.loads(r.read())
cmds = cfg["cameras"]["entrance"].get("ffmpeg_cmds", [])
for cmd in cmds:
    print(f"Roles: {cmd['roles']}")
    print(f"Cmd: {cmd['cmd']}")
    print()
