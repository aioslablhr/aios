#!/bin/bash
echo "Prometheus trailing slash test:"
curl -sS --connect-timeout 3 -D- "http://10.60.0.20:9090/prometheus/" 2>/dev/null | head -10
echo ""
echo "---"
echo "Prometheus no trailing slash test:"
curl -sS --connect-timeout 3 -D- "http://10.60.0.20:9090/prometheus" 2>/dev/null | head -10
echo ""
echo "---"
echo "Prometheus via Traefik trailing slash:"
curl -sS --connect-timeout 5 --max-time 10 -D- "https://monitor.socialbeesai.com/prometheus/" 2>/dev/null | head -10
echo ""
echo "---"
echo "Prometheus via Traefik no trailing slash:"
curl -sS --connect-timeout 5 --max-time 10 -D- "https://monitor.socialbeesai.com/prometheus" 2>/dev/null | head -10
