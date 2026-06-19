#!/bin/bash
docker exec aios-frigate sh -c 'grep -A 20 "def get_ffmpeg_arg_list" /opt/frigate/frigate/util/builtin.py'
