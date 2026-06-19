#!/bin/bash
docker exec aios-frigate sh -c '
echo "=== Looking for preset definitions ==="
grep -r "preset-rtsp-generic" /opt/frigate/ 2>/dev/null
echo ""
echo "=== Looking for rtsp_transport references ==="
grep -r "rtsp_transport" /opt/frigate/ 2>/dev/null
echo ""
echo "=== Looking for FRIGATE_ENV_VARS or ffmpeg presets ==="
find /opt/frigate -name "*.py" -exec grep -l "preset" {} \; 2>/dev/null
echo ""
echo "=== Any YAML configs with presets ==="
find /opt/frigate -name "*.yml" -o -name "*.yaml" 2>/dev/null
'
