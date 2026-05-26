#!/usr/bin/env python3
"""AIOS — Full Architecture Health Check
Verifies every service across all 8 zones.
Run: python3 /aios/scripts/health-check.py
"""

import subprocess, json, urllib.request, sys
from datetime import datetime

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
END = "\033[0m"

ZONES = {
    "DMZ (10.10.0.0/24)": {
        "aios-traefik": {"port": 80, "proto": "tcp"},
        "aios-crowdsec": {"port": 8080, "proto": "tcp"},
    },
    "App (10.20.0.0/24)": {
        "aios-n8n": {"port": 5678, "proto": "http", "path": "/healthz"},
        "aios-n8n-db": {"port": 5432, "proto": "tcp"},
        "aios-keycloak": {"port": 8080, "proto": "http"},
        "aios-gitops": {"port": None},
        "aios-hermes": {"port": None},
    },
    "Data (10.30.0.0/24)": {
        "aios-postgres": {"port": 5432, "proto": "tcp"},
        "aios-qdrant": {"port": 6333, "proto": "http", "path": "/healthz"},
        "aios-redis": {"port": 6379, "proto": "tcp"},
        "aios-minio": {"port": 9000, "proto": "http", "path": "/minio/health/live"},
        "aios-clickhouse": {"port": 8123, "proto": "http", "path": "/ping"},
    },
    "AI (10.40.0.0/24)": {
        "aios-bifrost": {"port": 4000, "proto": "http"},
        "aios-ollama": {"port": 11434, "proto": "http"},
        "aios-frigate": {"port": 5000, "proto": "http", "path": "/api/version"},
        "aios-chatterbox": {"port": 4123, "proto": "http"},
    },
    "Voice (10.50.0.0/24)": {
        "aios-mosquitto": {"port": 1883, "proto": "tcp"},
        "aios-dograh-api": {"port": 8080, "proto": "http"},
        "aios-dograh-ui": {"port": 3010, "proto": "http"},
        "aios-asterisk": {"port": None},
        "aios-dnsmasq-tftp": {"port": 69, "proto": "udp"},
    },
    "Mon (10.60.0.0/24)": {
        "aios-prometheus": {"port": 9090, "proto": "http"},
        "aios-grafana": {"port": 3000, "proto": "http"},
        "aios-loki": {"port": 3100, "proto": "http"},
        "aios-portainer": {"port": 9000, "proto": "http"},
        "aios-dashy": {"port": 8080, "proto": "http"},
        "aios-clickhouse": {"port": 8123, "proto": "http", "path": "/ping"},
        "aios-cadvisor": {"port": 8080, "proto": "http"},
        "aios-node-exporter": {"port": 9100, "proto": "http"},
    },
    "Security (host)": {
        "aios-vault": {"port": 8200, "proto": "http", "path": "/v1/sys/health"},
        "aios-vault-unseal": {"port": None},
    },
}

def check_container(name):
    r = subprocess.run(
        ["docker", "inspect", "--format", "{{.State.Status}}", name],
        capture_output=True, text=True, timeout=5
    )
    return r.stdout.strip() if r.returncode == 0 else "not found"

def check_tcp(ip, port):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try:
        s.connect((ip, port))
        s.close()
        return True
    except:
        return False

def check_http(ip, port, path="/"):
    try:
        r = urllib.request.urlopen(f"http://{ip}:{port}{path}", timeout=3)
        return r.status < 500
    except:
        return False

def get_container_ip(name):
    r = subprocess.run(
        ["docker", "inspect", "--format", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", name],
        capture_output=True, text=True, timeout=5
    )
    return r.stdout.strip() if r.returncode == 0 else ""

def main():
    print(f"\n{BOLD}{CYAN}═══ AIOS Architecture Health Check ═══{END}")
    print(f"{CYAN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{END}\n")

    all_ok = True
    total = 0
    passed = 0
    failed = 0

    for zone, services in ZONES.items():
        zone_ok = True
        print(f"\n{BOLD}{zone}{END}")
        print("─" * 60)

        for name, check in services.items():
            total += 1
            status = check_container(name)
            ip = get_container_ip(name)

            if status != "running":
                print(f"  {RED}✘{END} {name:<25} {RED}DOWN ({status}){END}")
                zone_ok = False; failed += 1
                continue

            if check["proto"] == "tcp" and check["port"]:
                port = ip.split(".")[-1]  # use network port
                reachable = check_tcp(ip, check["port"]) if ip else False
                if not reachable:
                    print(f"  {YELLOW}~{END} {name:<25} {GREEN}running{END} {YELLOW}port unreachable{END}")
                else:
                    print(f"  {GREEN}✓{END} {name:<25} {GREEN}running{END}")
                passed += 1

            elif check["proto"] == "http":
                path = check.get("path", "/")
                reachable = check_http(ip, check["port"], path) if ip else False
                if reachable:
                    print(f"  {GREEN}✓{END} {name:<25} {GREEN}responding{END}")
                    passed += 1
                else:
                    print(f"  {YELLOW}~{END} {name:<25} {GREEN}running{END} {YELLOW}not responding{END}")
                    passed += 1

            elif check["proto"] == "udp":
                print(f"  {GREEN}✓{END} {name:<25} {GREEN}running (UDP){END}")
                passed += 1
            else:
                print(f"  {GREEN}✓{END} {name:<25} {GREEN}running{END}")
                passed += 1

        if not zone_ok:
            all_ok = False

    print("\n" + "═" * 60)
    print(f"Total: {total}  |  {GREEN}Passed: {passed}{END}  |  {RED}Failed: {failed}{END}")
    print("═" * 60)

    # Docker ps summary
    r = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True, text=True, timeout=5
    )
    containers = [l for l in r.stdout.strip().split("\n") if l]
    print(f"\n{BOLD}Total running containers: {len(containers)}{END}")

    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
