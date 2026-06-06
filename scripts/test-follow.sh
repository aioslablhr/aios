#!/bin/bash
echo "=== Follow redirects ==="

echo "Prometheus:"
curl -sL --connect-timeout 5 --max-time 10 -o /dev/null -w "  %{http_code} -> %{url_effective}\n" https://monitor.socialbeesai.com/prometheus 2>/dev/null

echo "n8n direct:"
curl -sL --connect-timeout 5 --max-time 10 -o /dev/null -w "  %{http_code} -> %{url_effective}\n" https://n8n.socialbeesai.com 2>/dev/null

echo "Portainer:"
curl -sL --connect-timeout 5 --max-time 10 -o /dev/null -w "  %{http_code} -> %{url_effective}\n" https://monitor.socialbeesai.com/portainer 2>/dev/null

echo "Dograh:"
curl -sL --connect-timeout 5 --max-time 10 -o /dev/null -w "  %{http_code} -> %{url_effective}\n" https://voice.socialbeesai.com/dograh 2>/dev/null

echo "Grafana:"
curl -sL --connect-timeout 5 --max-time 10 -o /dev/null -w "  %{http_code} -> %{url_effective}\n" https://monitor.socialbeesai.com/grafana 2>/dev/null
