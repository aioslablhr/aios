#!/bin/bash
echo "=== New Dashy URLs ==="
for url in \
  "https://ai.socialbeesai.com" \
  "https://langfuse.socialbeesai.com" \
  "https://keycloak.socialbeesai.com" \
  "https://vault.socialbeesai.com" \
  "https://n8n.socialbeesai.com" \
  "https://voice.socialbeesai.com" \
  "https://data.socialbeesai.com/minio" \
  "https://monitor.socialbeesai.com/grafana" \
  "https://monitor.socialbeesai.com/prometheus" \
  "https://monitor.socialbeesai.com/portainer" \
  "https://admin.socialbeesai.com" \
  "https://socialbeesai.com"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$url" 2>/dev/null || echo "FAIL")
  printf "  %-45s %s\n" "$url" "$code"
done

echo ""
echo "=== Follow redirects ==="
for url in \
  "https://ai.socialbeesai.com" \
  "https://langfuse.socialbeesai.com" \
  "https://keycloak.socialbeesai.com" \
  "https://vault.socialbeesai.com"; do
  code=$(curl -sL -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 15 "$url" 2>/dev/null || echo "FAIL")
  printf "  %-45s %s\n" "$url" "$code"
done
