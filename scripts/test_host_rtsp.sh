#!/bin/bash
ffmpeg -rtsp_transport tcp -i "rtsp://admin:Lahore*999@10.0.0.51:554/cam/realmonitor?channel=1&subtype=1" -t 5 -f null - 2>&1 | tail -10
