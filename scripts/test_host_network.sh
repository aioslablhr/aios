#!/bin/bash
docker run --rm --network host alpine:latest sh -c '
apk add ffmpeg curl >/dev/null 2>&1
echo "=== TCP test ==="
ffmpeg -rtsp_transport tcp -i "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1" -t 3 -f null - 2>&1 | tail -3
echo "=== UDP test ==="
ffmpeg -rtsp_transport udp -i "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1" -t 3 -f null - 2>&1 | tail -3
echo "=== curl snapshot ==="
curl -s --digest -u "admin:Lahore*999" "http://10.0.0.51/cgi-bin/snapshot.cgi" -o /tmp/snap.jpg -w "%{http_code}"
' 2>&1
