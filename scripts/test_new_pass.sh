#!/bin/bash
docker run --rm --network host alpine:latest sh << 'SCRIPT'
apk add ffmpeg >/dev/null 2>&1
echo "=== RTSP UDP ==="
ffmpeg -rtsp_transport udp -i "rtsp://admin:Lahore999!@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1" -t 3 -f null - 2>&1 | tail -5
echo "=== RTSP TCP ==="
ffmpeg -rtsp_transport tcp -i "rtsp://admin:Lahore999!@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1" -t 3 -f null - 2>&1 | tail -5
echo "=== HTTP ==="
curl -s --digest -u "admin:Lahore999!" "http://10.0.0.51/cgi-bin/snapshot.cgi" -o /dev/null -w "HTTP: %{http_code}\n"
SCRIPT
