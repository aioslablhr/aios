#!/bin/bash
echo "=== Prometheus verbose ==="
curl -sS --connect-timeout 5 --max-time 10 -o /dev/null -w "HTTP %{http_code}\nLocation: %{redirect_url}\n" --max-time 10 "https://monitor.socialbeesai.com/prometheus" 2>/dev/null

echo ""
echo "=== Grafana verbose ==="
curl -sS --connect-timeout 5 --max-time 10 -o /dev/null -w "HTTP %{http_code}\nLocation: %{redirect_url}\n" --max-time 10 "https://monitor.socialbeesai.com/grafana" 2>/dev/null

echo ""
echo "=== Dograh verbose ==="
curl -sS --connect-timeout 5 --max-time 10 -o /dev/null -w "HTTP %{http_code}\nLocation: %{redirect_url}\n" --max-time 10 "https://voice.socialbeesai.com/dograh" 2>/dev/null

echo ""
echo "=== Direct Prometheus test ==="
curl -sS --connect-timeout 3 -o /dev/null -w "HTTP %{http_code}\n" http://10.60.0.20:9090/graph 2>/dev/null
