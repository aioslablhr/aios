#!/bin/bash
echo "Prometheus redirect details:"
curl -sS --connect-timeout 3 -D- http://10.60.0.20:9090/ 2>/dev/null | head -20
echo ""
echo "---"
curl -sS --connect-timeout 3 -D- "https://monitor.socialbeesai.com/prometheus/" 2>/dev/null | head -20
