#!/bin/bash
set -e
# Read UpliftAI API key from env
KEY=$(grep UPLIFTAI_API_KEY /aios/.env.aios | cut -d= -f2-)
echo "Key starts with: ${KEY:0:8}..."

# Direct call to UpliftAI API
curl -s -X POST "https://api.upliftai.org/v1/synthesis/text-to-speech" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "voiceId": "v_meklc281",
    "text": "Assalam-o-Alaikum! Main Zara bol rahi hoon. Imperium Developers mein aap ki kya madad kar sakti hoon?",
    "outputFormat": "MP3_22050_128"
  }' -o /tmp/uplift_direct.mp3

echo "Direct result:"
ls -la /tmp/uplift_direct.mp3
ffprobe -v quiet -show_entries format=duration,format_name /tmp/uplift_direct.mp3
echo "Size: $(wc -c < /tmp/uplift_direct.mp3) bytes"
