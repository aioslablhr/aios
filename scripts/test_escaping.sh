#!/bin/bash
# Test with escaped * to avoid any glob issues
echo "=== Escaped password test ==="
docker exec aios-frigate sh -c 'ffmpeg -rtsp_transport tcp -i "rtsp://admin:Lahore\*999@10.0.0.51:554/cam/realmonitor?channel=1\&subtype=1" -t 3 -f null - 2>&1' | tail -3
echo ""
echo "=== Test with ffmpeg 5.0 ==="
docker exec aios-frigate /usr/lib/ffmpeg/5.0/bin/ffmpeg -rtsp_transport tcp -i "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1" -t 3 -f null - 2>&1 | tail -3
echo ""
echo "=== Using echo + pipe to check what ffmpeg sees ==="
echo "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1" | docker exec -i aios-frigate cat
