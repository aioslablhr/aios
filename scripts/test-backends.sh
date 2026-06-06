#!/bin/bash
echo "=== Direct Backend Tests ==="
echo ""
echo "Portainer:"
curl -s -o /dev/null -w "  /         -> %{http_code}\n" --connect-timeout 3 http://10.60.0.50:9000/
curl -s -o /dev/null -w "  /portainer/ -> %{http_code}\n" --connect-timeout 3 http://10.60.0.50:9000/portainer/
echo ""
echo "Prometheus:"
curl -s -o /dev/null -w "  /           -> %{http_code}\n" --connect-timeout 3 http://10.60.0.20:9090/
curl -s -o /dev/null -w "  /prometheus/ -> %{http_code}\n" --connect-timeout 3 http://10.60.0.20:9090/prometheus/
echo ""
echo "Grafana:"
curl -s -o /dev/null -w "  /         -> %{http_code}\n" --connect-timeout 3 http://10.60.0.30:3000/
curl -s -o /dev/null -w "  /grafana/ -> %{http_code}\n" --connect-timeout 3 http://10.60.0.30:3000/grafana/
echo ""
echo "Dograh UI:"
curl -s -o /dev/null -w "  / -> %{http_code} %{redirect_url}\n" --connect-timeout 3 http://10.50.0.31:3010/
echo ""
echo "n8n:"
curl -s -o /dev/null -w "  /      -> %{http_code}\n" --connect-timeout 3 http://10.20.0.10:5678/
curl -s -o /dev/null -w "  /n8n/  -> %{http_code}\n" --connect-timeout 3 http://10.20.0.10:5678/n8n/
echo ""
echo "=== Traefik Live Routes ==="
docker exec aios-traefik wget -q -O- http://127.0.0.1:8080/api/http/routers 2>/dev/null | python3 -c "
import sys, json
routers = json.load(sys.stdin)
for r in routers:
    rule = r.get('rule','')
    svc = r.get('service','')
    status = r.get('status','')
    print(f'  {rule:<50} -> {svc} [{status}]')
" 2>/dev/null
