#!/bin/bash
# Test: does user_agent break RTSP auth?
echo "=== Test A: bare minimum UDP (should work) ==="
docker exec aios-frigate /usr/lib/ffmpeg/7.0/bin/ffmpeg \
  -rtsp_transport udp \
  -i "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1" \
  -t 2 -f null - 2>&1 | grep -E "frame|Error|401"

echo ""
echo "=== Test B: with user_agent ==="
docker exec aios-frigate /usr/lib/ffmpeg/7.0/bin/ffmpeg \
  -user_agent "FFmpeg Frigate/0.17.1-416a9b7" \
  -rtsp_transport udp \
  -i "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1" \
  -t 2 -f null - 2>&1 | grep -E "frame|Error|401"

echo ""
echo "=== Test C: with timeout ==="
docker exec aios-frigate /usr/lib/ffmpeg/7.0/bin/ffmpeg \
  -user_agent "FFmpeg Frigate/0.17.1-416a9b7" \
  -avoid_negative_ts make_zero \
  -fflags "+genpts+discardcorrupt" \
  -rtsp_transport udp \
  -timeout 10000000 \
  -use_wallclock_as_timestamps 1 \
  -i "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1" \
  -t 2 -f null - 2>&1 | grep -E "frame|Error|401"

echo ""
echo "=== Test D: with hide_banner + loglevel before -i ==="
docker exec aios-frigate /usr/lib/ffmpeg/7.0/bin/ffmpeg \
  -hide_banner -loglevel warning -threads 2 \
  -user_agent "FFmpeg Frigate/0.17.1-416a9b7" \
  -avoid_negative_ts make_zero \
  -fflags "+genpts+discardcorrupt" \
  -rtsp_transport udp \
  -timeout 10000000 \
  -use_wallclock_as_timestamps 1 \
  -i "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1" \
  -f rawvideo -pix_fmt yuv420p \
  -t 2 -f null - 2>&1 | grep -E "frame|Error|401"
