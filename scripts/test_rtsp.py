#!/usr/bin/env python3
"""Test Dahua camera RTSP with alternative approaches."""
import subprocess
import sys

tests = [
    # 1: ffmpeg raw * basic auth
    ("Test 1: raw *, auth_type basic", [
        "docker", "exec", "aios-frigate", "/usr/lib/ffmpeg/7.0/bin/ffmpeg",
        "-rtsp_transport", "tcp",
        "-auth_type", "basic",
        "-i", "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1",
        "-t", "2", "-f", "null", "-"
    ]),
    # 2: ffmpeg %2A basic auth
    ("Test 2: %2A, auth_type basic", [
        "docker", "exec", "aios-frigate", "/usr/lib/ffmpeg/7.0/bin/ffmpeg",
        "-rtsp_transport", "tcp",
        "-auth_type", "basic",
        "-i", "rtsp://admin:Lahore%2A999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1",
        "-t", "2", "-f", "null", "-"
    ]),
    # 3: ONVIF path
    ("Test 3: ONVIF path", [
        "docker", "exec", "aios-frigate", "/usr/lib/ffmpeg/7.0/bin/ffmpeg",
        "-rtsp_transport", "tcp",
        "-auth_type", "basic",
        "-i", "rtsp://admin:Lahore*999@10.0.0.51:554/onvif1",
        "-t", "2", "-f", "null", "-"
    ]),
    # 4: H.264 path
    ("Test 4: h264/ch1/main", [
        "docker", "exec", "aios-frigate", "/usr/lib/ffmpeg/7.0/bin/ffmpeg",
        "-rtsp_transport", "tcp",
        "-auth_type", "basic",
        "-i", "rtsp://admin:Lahore*999@10.0.0.51:554/h264/ch1/main/av_stream",
        "-t", "2", "-f", "null", "-"
    ]),
    # 5: H.264 sub
    ("Test 5: h264/ch1/sub", [
        "docker", "exec", "aios-frigate", "/usr/lib/ffmpeg/7.0/bin/ffmpeg",
        "-rtsp_transport", "tcp",
        "-auth_type", "basic",
        "-i", "rtsp://admin:Lahore*999@10.0.0.51:554/h264/ch1/sub/av_stream",
        "-t", "2", "-f", "null", "-"
    ]),
    # 6: wget result detail
    ("Test 6: wget CGI output", [
        "docker", "exec", "aios-frigate", "wget",
        "--user=admin", "--password=Lahore*999",
        "--auth-no-challenge",
        "-q", "-O", "-",
        "http://10.0.0.51/cgi-bin/magicBox.cgi?action=getSystemInfo"
    ]),
    # 7: UDP transport
    ("Test 7: UDP transport", [
        "docker", "exec", "aios-frigate", "/usr/lib/ffmpeg/7.0/bin/ffmpeg",
        "-rtsp_transport", "udp",
        "-i", "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1",
        "-t", "2", "-f", "null", "-"
    ]),
    # 8: H.265 path
    ("Test 8: h265/ch1/main", [
        "docker", "exec", "aios-frigate", "/usr/lib/ffmpeg/7.0/bin/ffmpeg",
        "-rtsp_transport", "tcp",
        "-auth_type", "basic",
        "-i", "rtsp://admin:Lahore*999@10.0.0.51:554/h265/ch1/main/av_stream",
        "-t", "2", "-f", "null", "-"
    ]),
    # 9: Try without auth in URL (ffmpeg will send empty auth)
    ("Test 9: no user in URL", [
        "docker", "exec", "aios-frigate", "/usr/lib/ffmpeg/7.0/bin/ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", "rtsp://10.0.0.51:554/cam/realmonitor?channel=1&subtype=1",
        "-t", "2", "-f", "null", "-"
    ]),
    # 10: Multiple transport tries (tcp + udp multicast)
    ("Test 10: TCP, user-agent workaround", [
        "docker", "exec", "aios-frigate", "/usr/lib/ffmpeg/7.0/bin/ffmpeg",
        "-rtsp_transport", "tcp",
        "-user_agent", "Mozilla/5.0 (compatible; Frigate/0.17)",
        "-auth_type", "basic",
        "-i", "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1",
        "-t", "2", "-f", "null", "-"
    ]),
    # 11: Main stream via UDP (record stream)
    ("Test 11: Main stream UDP", [
        "docker", "exec", "aios-frigate", "/usr/lib/ffmpeg/7.0/bin/ffmpeg",
        "-rtsp_transport", "udp",
        "-i", "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=0",
        "-t", "2", "-f", "null", "-"
    ]),
    # 12: ffmpeg 5.0 with UDP
    ("Test 12: ffmpeg 5.0 with UDP", [
        "docker", "exec", "aios-frigate", "/usr/lib/ffmpeg/5.0/bin/ffmpeg",
        "-rtsp_transport", "udp",
        "-i", "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1",
        "-t", "2", "-f", "null", "-"
    ]),
]

for name, cmd in tests:
    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = result.stderr[-800:] if result.stderr else result.stdout[-800:]
        relevant = []
        for line in output.split('\n'):
            line = line.strip()
            if any(kw in line.lower() for kw in ['error', '401', 'unauthorized', 'frame', 'stream', 'input', 'bad', 'invalid', 'authority']):
                relevant.append(line)
        for r in relevant:
            print(f"  {r}")
        if not relevant:
            print(f"  (output has no error/status lines)")
            print(f"  Last lines: {output[-200:]}")
    except subprocess.TimeoutExpired:
        print("  TIMEOUT")
    except Exception as e:
        print(f"  ERROR: {e}")
