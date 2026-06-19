#!/bin/bash
echo "=== TCP connectivity to camera ports from server ==="
for port in 554 80 443; do
  timeout 3 bash -c "echo >/dev/tcp/10.0.0.51/$port" 2>/dev/null && echo "Port $port: OPEN" || echo "Port $port: CLOSED/TIMEOUT"
done
echo ""
echo "=== IP routing to camera ==="
ip route get 10.0.0.51 2>/dev/null || route -n | grep 10.0.0.0
echo ""
echo "=== ARP entry for camera ==="
arp -n 10.0.0.51 2>/dev/null || arp -a | grep 10.0.0.51
echo ""
echo "=== Try curl with --digest --anyauth ==="
curl -v --anyauth -u "admin:Lahore*999" "http://10.0.0.51/cgi-bin/snapshot.cgi" -o /dev/null 2>&1 | tail -20
