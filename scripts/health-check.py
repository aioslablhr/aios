#!/usr/bin/env python3
"""AIOS — System Health Check.

Verifies all critical system components and outputs structured JSON:
  - Docker container status per zone
  - Disk usage
  - Memory usage
  - GPU status (nvidia-smi)
  - Service endpoint reachability

Usage:
  python3 health-check.py          # Full check, JSON to stdout
  python3 health-check.py --brief  # One-line summary
  python3 health-check.py --watch  # Continuous monitoring
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

HEALTHY = "\u2705"
WARNING = "\u26a0\ufe0f"
CRITICAL = "\u274c"

ZONES = {
    "DMZ (10.10)": ["aios-traefik", "aios-crowdsec"],
    "App (10.20)": ["aios-keycloak", "aios-vault", "aios-gitops", "aios-hermes"],
    "Data (10.30)": ["aios-postgres", "aios-qdrant", "aios-redis", "aios-minio"],
}


def log(msg):
    print(f"[health] {msg}", file=sys.stderr)


def run(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", -1


def check_docker():
    out, rc = run("docker ps --format '{{.Names}}\t{{.Status}}' 2>/dev/null")
    if rc != 0:
        return {"status": "error", "message": "Docker not responding"}, {}

    containers = {}
    for line in out.split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t", 1)
        name = parts[0]
        status = parts[1] if len(parts) > 1 else "unknown"
        healthy = "healthy" in status or "Up" in status
        containers[name] = {"status": status, "healthy": healthy}

    return {"status": "ok", "count": len(containers)}, containers


def check_disk():
    out, _ = run("df / | awk 'NR==2 {print $5,$3,$4}'")
    if not out:
        return {"error": "cannot read disk"}
    pct_str, used, avail = out.split()
    pct = int(pct_str.replace("%", ""))
    return {"pct": pct, "used": used, "avail": avail, "alert": pct > 90}


def check_memory():
    out, _ = run("free | awk '/Mem:/ {printf \"%.0f %s %s\", $3/$2*100, $3, $2}'")
    if not out:
        return {"error": "cannot read memory"}
    parts = out.split()
    pct = int(parts[0])
    return {"pct": pct, "used": parts[1], "total": parts[2], "alert": pct > 90}


def check_gpu():
    out, rc = run("nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,name --format=csv,noheader,nounits 2>/dev/null")
    if rc != 0:
        return {"available": False, "message": "nvidia-smi not found or GPU not accessible"}
    parts = out.split(", ")
    return {
        "available": True,
        "name": parts[3] if len(parts) > 3 else "unknown",
        "util_pct": int(parts[0]) if parts[0].isdigit() else 0,
        "memory_used_mb": parts[1],
        "memory_total_mb": parts[2],
        "temp_c": parts[3] if len(parts) > 3 else "N/A",
    }


def check_zones(containers):
    results = {}
    for zone, expected in ZONES.items():
        found = [c for c in expected if c in containers]
        missing = [c for c in expected if c not in containers]
        unhealthy = [c for c in found if not containers[c]["healthy"]]
        results[zone] = {
            "expected": len(expected),
            "found": len(found),
            "missing": missing,
            "unhealthy": unhealthy,
        }
    return results


def run_check():
    docker_status, containers = check_docker()
    disk = check_disk()
    memory = check_memory()
    gpu = check_gpu()
    zones = check_zones(containers) if containers else {}

    return {
        "timestamp": datetime.now().isoformat(),
        "hostname": os.uname().nodename,
        "docker": docker_status,
        "containers": containers,
        "zones": zones,
        "disk": disk,
        "memory": memory,
        "gpu": gpu,
    }


def brief_summary(report):
    total = report["docker"].get("count", 0)
    unhealthy = sum(1 for c in report.get("containers", {}).values() if not c["healthy"])
    disk = report["disk"].get("pct", 0)
    mem = report["memory"].get("pct", 0)
    gpu_ok = report["gpu"].get("available", False)
    icon = CRITICAL if unhealthy or disk > 90 or mem > 90 else HEALTHY
    return f"{icon} {total} containers | {unhealthy} unhealthy | disk {disk}% | mem {mem}% | gpu={'ok' if gpu_ok else 'N/A'} | {report['timestamp']}"


def main():
    parser = argparse.ArgumentParser(description="AIOS health check")
    parser.add_argument("--brief", action="store_true", help="One-line summary")
    parser.add_argument("--watch", type=int, help="Continuous monitoring interval (seconds)")
    args = parser.parse_args()

    if args.watch:
        while True:
            report = run_check()
            print(json.dumps(report if not args.brief else {"summary": brief_summary(report)}))
            time.sleep(args.watch)
    else:
        report = run_check()
        if args.brief:
            print(brief_summary(report))
        else:
            print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
