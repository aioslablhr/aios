#!/bin/bash
echo "=== Traefik Public Routes ==="
for url in \
  "https://socialbeesai.com" \
  "https://app.socialbeesai.com/n8n" \
  "https://n8n.socialbeesai.com" \
  "https://monitor.socialbeesai.com/grafana" \
  "https://monitor.socialbeesai.com/portainer" \
  "https://monitor.socialbeesai.com/prometheus" \
  "https://voice.socialbeesai.com/dograh" \
  "https://admin.socialbeesai.com" \
  "https://data.socialbeesai.com/minio"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$url" 2>/dev/null || echo "FAIL")
  echo "  $code $url"
done

echo ""
echo "=== Direct Backend Tests ==="
echo "Portainer:"
curl -s -o /dev/null -w "  / -> %{http_code}\n" --connect-timeout 3 http://10.60.0.50:9000/
echo "Prometheus:"
curl -s -o /dev/null -w "  / -> %{http_code}\n" --connect-timeout 3 http://10.60.0.20:9090/
echo "Grafana:"
curl -s -o /dev/null -w "  / -> %{http_code}\n" --connect-timeout 3 http://10.60.0.30:3000/
echo "Dograh UI:"
curl -s -o /dev/null -w "  / -> %{http_code}\n" --connect-timeout 3 http://10.50.0.31:3010/
echo "Dograh API:"
curl -s -o /dev/null -w "  / -> %{http_code}\n" --connect-timeout 3 http://10.50.0.30:8080/
echo "n8n:"
curl -s -o /dev/null -w "  / -> %{http_code}\n" --connect-timeout 3 http://10.20.0.10:5678/
echo "Frigate:"
curl -s -o /dev/null -w "  / -> %{http_code}\n" --connect-timeout 3 http://10.40.0.50:5000/api/version
echo "Chatterbox:"
curl -s -o /dev/null -w "  / -> %{http_code}\n" --connect-timeout 3 http://10.40.0.30:4123/
echo "Mosquitto:"
curl -s -o /dev/null -w "  / -> %{http_code}\n" --connect-timeout 3 http://10.50.0.20:1883/
