#!/usr/bin/env python3
"""Run ffmpeg with no shell to test RTSP UDP auth."""
import subprocess

cmd = [
    "docker", "exec", "aios-frigate",
    "/usr/lib/ffmpeg/7.0/bin/ffmpeg",
    "-rtsp_transport", "udp",
    "-i", "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1",
    "-t", "2", "-f", "null", "-"
]

print("Running:", " ".join(cmd))
result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
print("STDERR (last 20 lines):")
for line in result.stderr.strip().split('\n')[-20:]:
    print(f"  {line}")
print(f"\nReturn code: {result.returncode}")
