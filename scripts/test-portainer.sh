#!/bin/bash
echo "Portainer follow redirect:"
curl -sS -L --connect-timeout 5 --max-time 15 -o /dev/null -w "  %{http_code} -> %{url_effective}\n" "https://monitor.socialbeesai.com/portainer" 2>/dev/null
echo ""
echo "Portainer direct headers:"
curl -sS --connect-timeout 3 -D- "http://10.60.0.50:9000/" 2>/dev/null | head -10
