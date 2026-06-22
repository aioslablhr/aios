#!/bin/bash
echo "=== ALL PUBLIC ENDPOINTS ==="
echo ""
for url in \
  "https://socialbeesai.com" \
  "https://admin.socialbeesai.com" \
  "https://n8n.socialbeesai.com" \
  "https://ai.socialbeesai.com" \
  "https://langfuse.socialbeesai.com" \
  "https://keycloak.socialbeesai.com" \
  "https://vault.socialbeesai.com" \
  "https://voice.socialbeesai.com" \
  "https://data.socialbeesai.com/minio" \
  "https://grafana.socialbeesai.com" \
  "https://prometheus.socialbeesai.com" \
  "https://portainer.socialbeesai.com" \
  "https://cadvisor.socialbeesai.com" \
  "https://qdrant.socialbeesai.com/dashboard" \
  "https://clickhouse.socialbeesai.com" \
  "https://frigate.socialbeesai.com"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$url" 2>/dev/null || echo "FAIL")
  printf "  %-50s %s\n" "$url" "$code"
done

echo ""
echo "=== FOLLOW REDIRECTS ==="
for url in \
  "https://keycloak.socialbeesai.com" \
  "https://vault.socialbeesai.com" \
  "https://voice.socialbeesai.com" \
  "https://grafana.socialbeesai.com" \
  "https://prometheus.socialbeesai.com"; do
  code=$(curl -sL -o /dev/null -w "%{http_code} -> %{url_effective}" --connect-timeout 5 --max-time 15 "$url" 2>/dev/null || echo "FAIL")
  printf "  %-50s %s\n" "$url" "$code"
done
