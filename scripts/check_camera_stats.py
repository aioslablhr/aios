#!/usr/bin/env python3
import json, subprocess, sys

result = subprocess.run(
    ["curl", "-s", "http://10.0.0.100:5000/api/stats"],
    capture_output=True, text=True, timeout=10
)
stats = json.loads(result.stdout)
cam = stats.get("cameras", {}).get("entrance", {})
print(json.dumps(cam, indent=2))
