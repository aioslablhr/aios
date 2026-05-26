#!/bin/bash
# AIOS Architecture Verification
set -e

PASS=0
FAIL=0

check() {
    local name="$1"
    local expected="$2"
    local actual
    actual=$(sudo docker inspect --format '{{.State.Status}}' "$name" 2>/dev/null || echo "not found")
    if [ "$actual" = "$expected" ]; then
        echo -e "  \033[32m✓\033[0m $name"
        PASS=$((PASS+1))
    else
        echo -e "  \033[31m✘\033[0m $name ($actual, expected $expected)"
        FAIL=$((FAIL+1))
    fi
}

check_http() {
    local name="$1"
    local url="$2"
    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "$url" 2>/dev/null || echo "000")
    if [ "$code" != "000" ] && [ "$code" -lt 500 ]; then
        echo -e "  \033[32m✓\033[0m $name (HTTP $code)"
    else
        echo -e "  \033[33m~\033[0m $name (HTTP $code)"
    fi
}

echo ""
echo "============================================="
echo " AIOS — Architecture Verification"
echo " $(date)"
echo "============================================="

echo ""
echo "--- DMZ Zone ---"
check "aios-traefik" running
check "aios-crowdsec" running

echo ""
echo "--- App Zone ---"
check "aios-n8n" running
check "aios-n8n-db" running
check "aios-n8n-worker-1" running
check "aios-n8n-worker-2" running
check "aios-gitops" running
check "aios-hermes" running

echo ""
echo "--- Data Zone ---"
check "aios-postgres" running
check "aios-qdrant" running
check "aios-redis" running
check "aios-minio" running
check "aios-clickhouse" running

echo ""
echo "--- AI Zone ---"
check "aios-bifrost" running
check "aios-ollama" running
check "aios-frigate" running
check "aios-chatterbox" running

echo ""
echo "--- Voice Zone ---"
check "aios-mosquitto" running
check "aios-dograh-api" running
check "aios-dograh-ui" running
check "aios-asterisk" running
check "aios-dnsmasq-tftp" running

echo ""
echo "--- Mon Zone ---"
check "aios-prometheus" running
check "aios-grafana" running
check "aios-loki" running
check "aios-portainer" running
check "aios-dashy" running
check "aios-cadvisor" running
check "aios-node-exporter" running

echo ""
echo "--- Security ---"
check "aios-vault" running
check "aios-vault-unseal" running

echo ""
echo "--- HTTP Endpoints ---"
echo "(services with web UIs)"
check_http "n8n" "http://10.20.0.10:5678/healthz"
check_http "qdrant" "http://10.30.0.20:6333/healthz"
check_http "minio" "http://10.30.0.40:9000/minio/health/live"
check_http "prometheus" "http://10.60.0.20:9090/-/healthy"
check_http "grafana" "http://10.60.0.30:3000/api/health"
check_http "loki" "http://10.60.0.40:3100/ready"
check_http "portainer" "http://10.60.0.50:9000"
check_http "dashy" "http://10.60.0.70:8080"
check_http "bifrost" "http://10.40.0.10:4000/health"
check_http "ollama" "http://10.40.0.20:11434"
check_http "frigate" "http://10.40.0.50:5000/api/version"
check_http "vault" "http://127.0.0.1:8200/v1/sys/health"
check_http "langfuse" "http://10.60.0.10:3000/api/public/health"

echo ""
echo "--- Prometheus Targets ---"
sudo docker exec aios-prometheus wget -q -O- http://localhost:9090/api/v1/targets 2>/dev/null | \
  python3 -c "
import sys, json
d = json.load(sys.stdin)
for t in d['data']['activeTargets']:
    job = t['labels']['job']
    health = t['health']
    icon = '\033[32m✓\033[0m' if health == 'up' else '\033[31m✘\033[0m'
    print(f'  {icon} {job:<20} {health}')
" 2>/dev/null || echo "  (prometheus not responding yet)"

echo ""
echo "============================================="
echo -e " \033[32mPassed:\033[0m $PASS  \033[31mFailed:\033[0m $FAIL"
TOTAL=$(sudo docker ps -q | wc -l)
echo -e " \033[36mRunning containers:\033[0m $TOTAL"
echo "============================================="
echo ""
