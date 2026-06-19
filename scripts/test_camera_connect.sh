#!/bin/bash
# Test 1: Curl with %2A encoded password 
echo "=== Test 1: Digest auth with URL-encoded password ==="
docker exec aios-frigate sh -c "curl -s --digest -u 'admin:Lahore%2A999' 'http://10.0.0.51/cgi-bin/magicBox.cgi?action=getSystemInfo' 2>&1" | head -c 400
echo ""
echo ""
# Test 2: Curl with raw * password
echo "=== Test 2: Digest auth with raw * password ==="
docker exec aios-frigate sh -c "curl -s --digest -u 'admin:Lahore*999' 'http://10.0.0.51/cgi-bin/magicBox.cgi?action=getSystemInfo' 2>&1" | head -c 400
echo ""
echo ""
# Test 3: Try without --digest (Basic)
echo "=== Test 3: Basic auth with URL-encoded password ==="
docker exec aios-frigate sh -c "curl -s -u 'admin:Lahore%2A999' 'http://10.0.0.51/cgi-bin/magicBox.cgi?action=getSystemInfo' 2>&1" | head -c 400
echo ""
echo ""
# Test 4: Try ffmpeg 5.0
echo "=== Test 4: ffmpeg 5.0 on main stream ==="
docker exec aios-frigate sh -c "/usr/lib/ffmpeg/5.0/bin/ffmpeg -rtsp_transport tcp -i 'rtsp://admin:Lahore%2A999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=0' -t 3 -f null - 2>&1" | grep -E "Error|frame|Input"
echo ""
