#!/bin/bash
# Test UDP with properly quoted args
docker exec aios-frigate /usr/lib/ffmpeg/7.0/bin/ffmpeg \
  -rtsp_transport udp \
  -i "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1" \
  -t 2 -f null - 2>&1 | tail -10
