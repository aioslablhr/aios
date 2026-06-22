#!/bin/bash
echo "Prometheus paths:"
curl -sS --connect-timeout 5 --max-time 10 -o /dev/null -w "  /prometheus/ -> %{http_code}\n" "https://prometheus.socialbeesai.com/" 2>/dev/null
curl -sS --connect-timeout 5 --max-time 10 -o /dev/null -w "  /prometheus/graph -> %{http_code}\n" "https://prometheus.socialbeesai.com/graph" 2>/dev/null
curl -sS --connect-timeout 5 --max-time 10 -o /dev/null -w "  /prometheus/targets -> %{http_code}\n" "https://prometheus.socialbeesai.com/targets" 2>/dev/null
echo ""
echo "Direct Prometheus paths:"
curl -sS --connect-timeout 3 -o /dev/null -w "  / -> %{http_code}\n" http://10.60.0.20:9090/ 2>/dev/null
curl -sS --connect-timeout 3 -o /dev/null -w "  /graph -> %{http_code}\n" http://10.60.0.20:9090/graph 2>/dev/null
curl -sS --connect-timeout 3 -o /dev/null -w "  /targets -> %{http_code}\n" http://10.60.0.20:9090/targets 2>/dev/null
echo ""
echo "Grafana paths:"
curl -sS --connect-timeout 5 --max-time 10 -o /dev/null -w "  /grafana/ -> %{http_code}\n" "https://grafana.socialbeesai.com/" 2>/dev/null
curl -sS --connect-timeout 5 --max-time 10 -o /dev/null -w "  /grafana/login -> %{http_code}\n" "https://grafana.socialbeesai.com/login" 2>/dev/null
echo ""
echo "Dograh UI paths:"
curl -sS --connect-timeout 5 --max-time 10 -o /dev/null -w "  / -> %{http_code}\n" "https://voice.socialbeesai.com/" 2>/dev/null
curl -sS --connect-timeout 5 --max-time 10 -o /dev/null -w "  /auth/login -> %{http_code}\n" "https://voice.socialbeesai.com/auth/login" 2>/dev/null
