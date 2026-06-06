#!/bin/bash
echo "Prometheus with prefix (/prometheus/...) direct:"
curl -sS --connect-timeout 3 -D- http://10.60.0.20:9090/prometheus/ 2>/dev/null | head -20
echo ""
echo "---"
echo "API v1 targets:"
curl -sS --connect-timeout 3 http://10.60.0.20:9090/api/v1/targets 2>/dev/null | head -100
echo ""
echo "---"
echo "API v1 targets with prefix:"
curl -sS --connect-timeout 3 http://10.60.0.20:9090/prometheus/api/v1/targets 2>/dev/null | head -100
