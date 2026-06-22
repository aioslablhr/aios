#!/bin/bash
echo "=== Testing ALL Dashy URLs ==="
echo ""

test_url() {
  local url=$1
  local label=$2
  local code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$url" 2>/dev/null || echo "FAIL")
  printf "  %-30s %s\n" "$label" "$code"
}

test_url "https://chat.socialbeesai.com" "Open WebUI"
test_url "https://langfuse.socialbeesai.com" "Langfuse"
test_url "https://app.socialbeesai.com/n8n" "n8n"
test_url "https://app.socialbeesai.com/flowise" "Flowise"
test_url "https://data.socialbeesai.com" "Supabase"
test_url "https://data.socialbeesai.com/minio" "MinIO"
test_url "https://grafana.socialbeesai.com" "Grafana"
test_url "https://prometheus.socialbeesai.com" "Prometheus"
test_url "https://portainer.socialbeesai.com" "Portainer"
test_url "https://voice.socialbeesai.com" "Dograh"
test_url "https://admin.socialbeesai.com" "Traefik Dashboard"
test_url "https://admin.socialbeesai.com/keycloak" "Keycloak Admin"
test_url "https://admin.socialbeesai.com/vault" "Vault UI"
test_url "https://n8n.socialbeesai.com" "n8n Direct"
test_url "https://ai.socialbeesai.com/bifrost" "Bifrost"
test_url "https://www.socialbeesai.com" "WWW"
test_url "https://socialbeesai.com" "Dashy"

echo ""
echo "=== Direct backend tests ==="
test_url "http://10.60.0.10:3000" "Langfuse direct"
test_url "http://10.20.0.50:8200" "Vault direct"
test_url "http://10.20.0.40:8080" "Keycloak direct"
test_url "http://10.30.0.10:8000" "Supabase direct"
test_url "http://10.40.0.10:4000" "Bifrost direct"
test_url "http://10.40.0.20:3000" "Ollama/librechat direct"
