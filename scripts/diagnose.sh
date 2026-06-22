#!/bin/bash
echo "=== Container Status ==="
docker ps --format "table {{.Names}}\t{{.Status}}"

echo ""
echo "=== Testing Internal Endpoints ==="
for target in \
  "n8n:10.20.0.10:5678/healthz" \
  "qdrant:10.30.0.20:6333/healthz" \
  "minio:10.30.0.40:9000/minio/health/live" \
  "prometheus:10.60.0.20:9090/-/healthy" \
  "grafana:10.60.0.30:3000/api/health" \
  "portainer:10.60.0.50:9000" \
  "dashy:10.60.0.70:8080" \
  "bifrost:10.40.0.10:4000/health" \
  "ollama:10.40.0.20:11434" \
  "frigate:10.40.0.50:5000/api/version" \
  "chatterbox:10.40.0.30:4123" \
  "dograh-api:10.50.0.30:8080" \
  "dograh-ui:10.50.0.31:3010" \
  "langfuse:10.60.0.10:3000/api/public/health"; do
  name=$(echo "$target" | cut -d: -f1)
  ip=$(echo "$target" | cut -d: -f2)
  port=$(echo "$target" | cut -d: -f3 | cut -d/ -f1)
  path=$(echo "$target" | cut -d/ -f2- -s)
  if [ -n "$path" ]; then
    code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 --max-time 5 "http://${ip}:${port}/${path}" 2>/dev/null || echo "FAIL")
  else
    code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 --max-time 5 "http://${ip}:${port}" 2>/dev/null || echo "FAIL")
  fi
  if [ "$code" = "FAIL" ]; then
    echo "  ✘ $name (${ip}:${port}) - CONNECTION FAILED"
  elif [ "$code" -ge 200 ] && [ "$code" -lt 500 ]; then
    echo "  ✓ $name (${ip}:${port}) - HTTP $code"
  else
    echo "  ~ $name (${ip}:${port}) - HTTP $code"
  fi
done

echo ""
echo "=== Testing Public Traefik Routes ==="
for url in \
  "https://socialbeesai.com" \
  "https://app.socialbeesai.com/n8n" \
  "https://grafana.socialbeesai.com" \
  "https://portainer.socialbeesai.com" \
  "https://prometheus.socialbeesai.com" \
  "https://voice.socialbeesai.com/dograh" \
  "https://admin.socialbeesai.com" \
  "https://data.socialbeesai.com/minio"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$url" 2>/dev/null || echo "FAIL")
  if [ "$code" = "FAIL" ]; then
    echo "  ✘ $url - CONNECTION FAILED"
  else
    echo "  $code $url"
  fi
done

echo ""
echo "=== Traefik Recent Errors ==="
docker logs aios-traefik --tail 30 2>&1 | grep -i "error\|ERR\|Failed\|500" | tail -10

echo ""
echo "=== n8n Logs ==="
docker logs aios-n8n --tail 10 2>&1

echo ""
echo "=== dograh-api Logs ==="
docker logs aios-dograh-api --tail 10 2>&1
