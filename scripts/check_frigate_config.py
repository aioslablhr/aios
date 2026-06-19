#!/usr/bin/env python3
# Check what command Frigate actually generated for the entrance camera
import json, subprocess

# Get config
r = subprocess.run(["curl", "-s", "http://10.0.0.100:5000/api/config"], capture_output=True, text=True, timeout=10)
cfg = json.loads(r.stdout)

cam = cfg["cameras"]["entrance"]
print("Camera name:", cam.get("name"))
print("Enabled:", cam.get("enabled"))

ff = cam.get("ffmpeg", {})
print("\n=== Camera-level ffmpeg config ===")
print(f"input_args: {ff.get('input_args')}")
print(f"hwaccel_args: {ff.get('hwaccel_args')}")

for inp in ff.get("inputs", []):
    print(f"\n=== Input: {inp['roles']} ===")
    print(f"path: {inp['path'][:60]}...")
    print(f"input_args: {inp.get('input_args')}")
    print(f"global_args: {inp.get('global_args')}")
    print(f"hwaccel_args: {inp.get('hwaccel_args')}")

# Check the global ffmpeg config  
print("\n=== Global ffmpeg ===")
print(f"input_args: {cfg.get('ffmpeg', {}).get('input_args')}")
print(f"hwaccel_args: {cfg.get('ffmpeg', {}).get('hwaccel_args')}")
