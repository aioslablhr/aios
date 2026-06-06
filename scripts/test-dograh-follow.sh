#!/bin/bash
echo "Dograh follow redirect:"
curl -sS --connect-timeout 5 --max-time 10 -D- "https://voice.socialbeesai.com/dograh" 2>/dev/null | head -10
echo ""
echo "---"
curl -sS -L --connect-timeout 5 --max-time 15 -o /dev/null -w "Final: %{http_code} -> %{url_effective}\n" "https://voice.socialbeesai.com/dograh" 2>/dev/null
echo ""
echo "Direct:"
curl -sS --connect-timeout 3 -D- "http://10.50.0.31:3010/" 2>/dev/null | head -10
echo ""
echo "---"
curl -sS -L --connect-timeout 3 --max-time 10 -o /dev/null -w "Direct Final: %{http_code} -> %{url_effective}\n" "http://10.50.0.31:3010/" 2>/dev/null
