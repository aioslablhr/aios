#!/usr/bin/env python3
"""Test RTSP via ffmpeg from server host using subprocess."""
import subprocess, sys, os

cmd_udp = [
    "docker", "run", "--rm", "--network", "host", "alpine:latest",
    "sh", "-c",
    "apk add ffmpeg >/dev/null 2>&1; ffmpeg -rtsp_transport udp -i 'rtsp://admin:Lahore999!@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1' -t 3 -f null - 2>&1 | tail -5"
]

cmd_tcp = [
    "docker", "run", "--rm", "--network", "host", "alpine:latest",
    "sh", "-c",
    "apk add ffmpeg >/dev/null 2>&1; ffmpeg -rtsp_transport tcp -i 'rtsp://admin:Lahore999!@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1' -t 3 -f null - 2>&1 | tail -5"
]

for label, cmd in [("UDP", cmd_udp), ("TCP", cmd_tcp)]:
    print(f"\n=== {label} ===")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    print(r.stdout or r.stderr)
