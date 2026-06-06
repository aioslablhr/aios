#!/bin/bash
echo "Grafana trailing slash test:"
curl -sS --connect-timeout 5 --max-time 10 -D- "https://monitor.socialbeesai.com/grafana/" 2>/dev/null | head -10
echo ""
echo "---"
echo "Grafana no trailing slash:"
curl -sS --connect-timeout 5 --max-time 10 -D- "https://monitor.socialbeesai.com/grafana" 2>/dev/null | head -10
echo ""
echo "---"
echo "Grafana login:"
curl -sS --connect-timeout 5 --max-time 10 -D- "https://monitor.socialbeesai.com/grafana/login" 2>/dev/null | head -15
