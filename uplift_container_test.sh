#!/bin/bash
docker exec aios-tts-router bash -c \
  'curl -s -X POST "https://api.upliftai.org/v1/synthesis/text-to-speech" \
    -H "Authorization: Bearer $UPLIFTAI_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"voiceId\":\"v_meklc281\",\"text\":\"Assalam-o-Alaikum! Main Zara bol rahi hoon.\",\"outputFormat\":\"MP3_22050_128\"}" \
    -o /tmp/uplift_container.mp3 && ls -la /tmp/uplift_container.mp3 && file /tmp/uplift_container.mp3 && ffprobe -v quiet -show_entries format=duration,format_name /tmp/uplift_container.mp3 2>/dev/null || echo "ffprobe not available"'
