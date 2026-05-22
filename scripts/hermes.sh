#!/bin/sh
# Hermes Agent — 24/7 autonomous ops for AIOS
# Monitors Docker containers, auto-restarts unhealthy ones,
# checks disk/memory/GPU, writes structured JSON to stdout.

HERMES_LOG="/dev/stdout"
HEALTH_FILE="/tmp/hermes-health.json"
CHECK_INTERVAL=60

log() {
  local level="$1"
  shift
  echo "[Hermes] $(date -Iseconds) [$level] $*" > "$HERMES_LOG"
}

check_containers() {
  local restarted=0

  for name in $(docker ps --format '{{.Names}}' 2>/dev/null); do
    local health
    health=$(docker inspect --format='{{.State.Health.Status}}' "$name" 2>/dev/null || echo "no-healthcheck")

    if [ "$health" = "unhealthy" ]; then
      log "WARN" "$name is UNHEALTHY — restarting"
      docker restart "$name" 2>/dev/null && restarted=$((restarted + 1))
    elif [ "$health" = "no-healthcheck" ]; then
      local status
      status=$(docker inspect --format='{{.State.Status}}' "$name")
      if [ "$status" != "running" ]; then
        log "WARN" "$name is $status — restarting"
        docker restart "$name" 2>/dev/null && restarted=$((restarted + 1))
      fi
    fi
  done

  echo "$restarted"
}

probe_all() {
  local containers
  containers=$(docker ps --format '{{.Names}}' 2>/dev/null | wc -l)

  local disk_pct
  disk_pct=$(df / | awk 'NR==2 {print $5}' | tr -d '%')

  local mem_pct
  mem_pct=$(free | awk '/Mem:/ {printf "%d", $3/$2 * 100}')

  local gpu_info
  if command -v nvidia-smi >/dev/null 2>&1; then
    gpu_info=$(nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits 2>/dev/null || echo "N/A,N/A,N/A,N/A")
  else
    gpu_info="N/A (no nvidia-smi)"
  fi

  local restarted
  restarted=$(check_containers)

  if command -v jq >/dev/null 2>&1; then
    jq -n \
      --arg ts "$(date -Iseconds)" \
      --argjson containers "$containers" \
      --argjson disk "$disk_pct" \
      --argjson mem "$mem_pct" \
      --arg gpu "$gpu_info" \
      --argjson restarted "$restarted" \
      '{timestamp: $ts, containers: $containers, disk_pct: $disk, mem_pct: $mem, gpu: $gpu, restarted: $restarted}' \
      2>/dev/null > "$HEALTH_FILE" || true
    cat "$HEALTH_FILE" 2>/dev/null > "$HERMES_LOG" || true
  fi

  if [ "$restarted" -gt 0 ]; then
    log "ALERT" "Restarted $restarted containers this cycle"
  fi

  if [ "$disk_pct" -gt 90 ]; then
    log "ALERT" "Disk at ${disk_pct}% — threshold 90%"
  fi

  if [ "$mem_pct" -gt 90 ]; then
    log "ALERT" "Memory at ${mem_pct}% — threshold 90%"
  fi
}

log "INFO" "Hermes Agent v1.0 starting — interval ${CHECK_INTERVAL}s"

while true; do
  probe_all
  sleep "$CHECK_INTERVAL"
done
