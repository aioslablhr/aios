#!/usr/bin/env python3
"""Try multiple auth approaches after potential lockout."""
import subprocess

tests = [
    ("UDP + %2A", [
        "docker", "exec", "aios-frigate",
        "/usr/lib/ffmpeg/7.0/bin/ffmpeg",
        "-rtsp_transport", "udp",
        "-i", "rtsp://admin:Lahore%2A999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1",
        "-t", "2", "-f", "null", "-"
    ]),
    ("UDP + raw *", [
        "docker", "exec", "aios-frigate",
        "/usr/lib/ffmpeg/7.0/bin/ffmpeg",
        "-rtsp_transport", "udp",
        "-i", "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1",
        "-t", "2", "-f", "null", "-"
    ]),
    ("TCP + %2A", [
        "docker", "exec", "aios-frigate",
        "/usr/lib/ffmpeg/7.0/bin/ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", "rtsp://admin:Lahore%2A999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1",
        "-t", "2", "-f", "null", "-"
    ]),
    ("TCP + raw *", [
        "docker", "exec", "aios-frigate",
        "/usr/lib/ffmpeg/7.0/bin/ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1",
        "-t", "2", "-f", "null", "-"
    ]),
]

for name, cmd in tests:
    print(f"\n=== {name} ===")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        for line in result.stderr.split('\n'):
            if any(kw in line.lower() for kw in ['frame=', '401', 'unauthorized', 'error opening']):
                print(f"  {line.strip()}")
    except subprocess.TimeoutExpired:
        print("  TIMEOUT (might mean it's working!)")
    except Exception as e:
        print(f"  ERROR: {e}")
