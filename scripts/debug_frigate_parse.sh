#!/bin/bash
docker exec aios-frigate sh -c '
python3 -c "
import json
from frigate.config.config import FrigateConfig
import yaml

# Load the actual config file
with open(\"/config/config.yml\", \"r\") as f:
    raw = yaml.safe_load(f)

# Parse it through FrigateConfig
config = FrigateConfig.parse_config(raw)

# Check the entrance camera
cam = config.cameras.get(\"entrance\")
if cam:
    print(\"Camera ffmpeg input_args:\", cam.ffmpeg.input_args)
    for inp in cam.ffmpeg.inputs:
        print(f\"  Input roles={inp.roles} input_args={inp.input_args}\")
        print(f\"  Input path: {inp.path[:60]}...\")

# Check global ffmpeg
print(\"Global ffmpeg input_args:\", config.ffmpeg.input_args)
"
'
