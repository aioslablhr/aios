#!/usr/bin/env python3
from frigate.ffmpeg_presets import parse_preset_input, PRESETS_INPUT

print("Test 1: preset-rtsp-udp")
r = parse_preset_input("preset-rtsp-udp", 5)
print(f"Result: {r}")

print("\nTest 2: empty list []")
r = parse_preset_input([], 5)
print(f"Result: {r}")

print("\nTest 3: raw -rtsp_transport udp")
r = parse_preset_input("-rtsp_transport udp", 5)
print(f"Result: {r}")

print("\nTest 4: Check PRESETS_INPUT keys with udp")
keys = [k for k in PRESETS_INPUT.keys() if "udp" in k]
print(f"UDP keys: {keys}")
print(f"preset-rtsp-udp exists: {'preset-rtsp-udp' in PRESETS_INPUT}")
