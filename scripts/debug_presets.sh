#!/bin/bash
# Debug what input_args Frigate actually resolves
docker exec aios-frigate sh -c '
python3 -c "
from frigate.ffmpeg_presets import parse_preset_input, PRESETS_INPUT
from frigate.config.camera.ffmpeg import FFMPEG_INPUT_ARGS_DEFAULT

# Test 1: What does preset-rtsp-udp resolve to?
print(\"=== Test 1: preset-rtsp-udp ===\")
result = parse_preset_input(\"preset-rtsp-udp\", 5)
print(f\"Result: {result}\")

# Test 2: What does an empty list resolve to?
print(\"=== Test 2: empty list [] ===\")
result = parse_preset_input([], 5)
print(f\"Result: {result}\")

# Test 3: What does -rtsp_transport udp resolve to?
print(\"=== Test 3: raw args ===\")
result = parse_preset_input(\"-rtsp_transport udp\", 5)
print(f\"Result: {result}\")

# Test 4: Does preset-rtsp-udp exist in PRESETS_INPUT?
print(\"=== Test 4: Is preset-rtsp-udp in PRESETS_INPUT? ===\")
has = "preset-rtsp-udp" in PRESETS_INPUT
print(f"Exists: {has}")
print(f\"Keys with udp: {[k for k in PRESETS_INPUT.keys() if \"udp\" in k]}\")
"
'
