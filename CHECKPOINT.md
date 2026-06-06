# AIOS — Session Checkpoint

**Version:** 4.12
**Date:** June 6, 2026
**Branch:** main
**Last commit:** (pending — bifrost auth + config fix)

---

## Container Status (Server)

### Running (44 — all services healthy or starting)
aios-traefik, aios-postgres, aios-redis, aios-qdrant, aios-minio, aios-clickhouse, aios-ollama, aios-bifrost, aios-langfuse, aios-docling, aios-mem0, aios-asterisk, aios-dnsmasq-tftp, aios-knowledge-ingest, aios-knowledge-compile, aios-dograh-api, aios-dograh-ui, aios-tts-router, aios-chatterbox, aios-kokoro, aios-xtts-urdu, aios-n8n, aios-n8n-worker-1, aios-n8n-worker-2, aios-n8n-db, aios-flowise, aios-open-webui, aios-keycloak, aios-mcp, aios-vault, aios-vault-unseal, aios-grafana, aios-portainer, aios-dashy, aios-prometheus, aios-cadvisor, aios-node-exporter, aios-loki, aios-crowdsec, aios-frigate, aios-mosquitto, aios-gitops, aios-hermes, aios-data-minio-proxy, aios-data-qdrant-proxy

### Known Issues
- Chatterbox: runs with model loaded on CUDA but Docker healthcheck marks unhealthy
- Keycloak: health: starting (takes ~2min to become healthy)
- Hermes: running (was exit 126, fixed via chmod)
- WireGuard: Created state (sysctl `net.ipv4.conf.all.src_valid_mark` not allowed in host network namespace — pre-existing, user wants to keep)

### Written but NOT started
- Nextcloud (10.70.0.30), Odoo (10.70.0.20), Metabase (10.70.0.40) — docker-compose-apps.yml exists, never started

---

## What's Done This Session (June 6 — Stack Recovery + Bifrost Fix)

### 1. Stack Recovery — All 45 Containers Running ✅
- Diagnosed: 0 containers running (stack never started after server reboot)
- Started all containers, manually fixed 15 stuck in "Created" state
- Created & enabled `aios-stack.service` systemd unit for auto-start on boot

### 2. Bifrost Auth — Fixed ✅
- Root cause: Master key `sk-aios-master-admin-key-change-me` not hashed/seeded into `LiteLLM_VerificationToken` table in PostgreSQL
- Dropped stale token tables → Bifrost recreated via migration → inserted SHA256 hash of master key directly into DB
- Verified: `curl /v1/chat/completions` with Bearer token returns clean LLM responses through OpenRouter free tier (Gemma-4-31b-it)

### 3. Bifrost Config.yaml — Fixed ✅
- Changed env var syntax from `${OPENROUTER_API_KEY}` → `os.environ/OPENROUTER_API_KEY` (LiteLLM native syntax)
- Removed invalid `disable_auth: true` setting (doesn't exist in LiteLLM v1.82.6)
- Set `master_key: os.environ/BIFROST_ADMIN_KEY` (was `${BIFROST_ADMIN_KEY:-sk-aios-master}`)

### 4. docker-compose-aios.yml — Fixed ✅
- Removed `DISABLE_AUTH: "true"` from bifrost env
- Added `${LANGFUSE_PUBLIC_KEY:-}` / `${LANGFUSE_SECRET_KEY:-}` — defaults to blank to suppress compose warnings
- Added `${WEBUI_SECRET_KEY:-change-me-in-env}` — default value to suppress compose warning
- Added `kokoro` service definition — was running as orphan, now tracked by compose
- Fixed `KC_PROXY` duplicate key in keycloak service definition

### 5. Hermes — Fixed ✅
- `chmod +x /aios/scripts/hermes.sh` resolved exit 126 Permission denied
- Container now runs cleanly

### 6. Systemd Auto-Start — Added ✅
- `/etc/systemd/system/aios-stack.service` — `docker compose up -d` on boot
- Enabled, tested

### 7. Compose Warnings — Cleaned ✅
- No more `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, or `WEBUI_SECRET_KEY` warnings
- No more orphan container warnings (kokoro now defined in compose)
- Single warning remaining: WireGuard sysctl (known, pre-existing)

---

## Pending (Not Started / Not Working)

| Item | Priority | Status |
|------|----------|--------|
| Pull Ollama models (qalb-1.0-8b, llava:7b) | Medium | ❌ Only nomic-embed-text loaded |
| FOSS apps start (Nextcloud, Odoo, Metabase) | Medium | ❌ `docker compose -f docker-compose-apps.yml up -d` never run |
| Chatterbox healthcheck fix | Low | ❌ Container works, healthcheck endpoint missing |
| WireGuard peer config retrieval | Low | ❌ Config auto-generated but sysctl blocks start |
| Nightly backup cron | Low | ❌ Script exists (`backup.py`) but no cron job |
| First n8n workflow (AI employee) | Deferred | ❌ Blocked on infra completion |

---

## Voice Pipeline Architecture

```
Caller → SIP Trunk → Asterisk → AGI (ai-agent.agi)
  → Record WAV → POST to n8n webhook (/webhook/ai-agent)
    → Whisper STT (Ollama/Bifrost)
    → Qalb LLM (via Bifrost → Ollama)
    → TTS Router (Urdu→XTTS, English→Chatterbox, fallback→Kokoro)
  → Return WAV → Play to Caller
  → Loop for conversation
```

- **Asterisk Ext 102**: AI Agent — triggers `ai-agent.agi` AGI script
- **Asterisk Ext 9000**: Cisco 7962G phone (registered, test calls)
- **Asterisk Ext 101**: Softphone on 10.0.0.11 (active)
- **Dograh** (10.50.0.30:8000): Full voice agent orchestration with ARI+WebSocket integration. API prefix `/api/v1`, telephony routes at `/api/v1/telephony/initiate` and WebSocket at `/ws/ari`. Requires n8n workflow for full pipeline.
- **n8n webhook**: `/webhook/ai-agent` on n8n (10.20.0.10:5678) — **not created yet**, needs workflow

## How to Test the Pipeline

### Level 1 — Component Tests (no phone, immediate)
```bash
# Test Urdu TTS
curl http://10.40.0.32:8020/v1/tts -d '{"text":"السلام علیکم","language":"ur"}' -o /tmp/xtts-test.wav

# Test TTS Router (auto Urdu detection)
curl http://10.40.0.33:8030/v1/audio/speech \
  -d '{"input":"السلام علیکم، آپ کیسے ہیں؟"}' -o /tmp/router-test.wav

# Test Bifrost LLM (via OpenRouter free tier)
curl http://10.40.0.10:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-aios-master-admin-key-change-me" \
  -d '{"model":"general-reasoning","messages":[{"role":"user","content":"say hi"}]}'

# Test all 3 TTS backends via health check
curl http://10.40.0.33:8030/health
```

### Level 2 — Phone Call Test
- Pick up Cisco 7962G (Ext 9000) → call 101 → talks to softphone on 10.0.0.11 (basic SIP test)
- Pick up Cisco → call 103/104 → tests other registered phones
- Requires active n8n `ai-agent` webhook for Ext 102 (AI Agent) to work

### Level 3 — Full AI Voice Conversation
1. Create n8n workflow: Receive WAV → Whisper STT → Bifrost/Qalb LLM → TTS Router → Return WAV
2. Save as webhook `/webhook/ai-agent`
3. Call Ext 102 from any phone → full Urdu voice conversation with Qalb

### Level 4 — Dograh Integration
- Configure Dograh with Asterisk ARI provider
- Use Dograh REST API or UI (10.50.0.31:3010) for outbound campaigns and advanced voice flows

## Key Architectural Decisions

1. **GPU limitation**: Quadro M4000 (Maxwell CC 5.0) maxes at NVIDIA driver 470, CUDA 11.4. No CUDA 12.x support. Ollama bundles its own CUDA 12.x and works anyway. Other containers (XTTS, Chatterbox) need explicit handling.
2. **Qalb GGUF**: 8B model at Q4_K_M (4.92GB) fits in 8GB VRAM alongside other models. FP16 (16GB) is too large.
3. **XTTS CPU-only**: Using CPU PyTorch because CUDA 12.x not available. TTS inference is fast enough on modern CPU.
4. **TTS pipeline**: Urdu → XTTS, English → Chatterbox (GPU), fallback → Kokoro (CPU), routed by TTS Router (10.40.0.33:8030).
5. **Voice pipeline**: Asterisk AGI → n8n webhook → Whisper/Qalb/TTS → response WAV. Dograh provides advanced orchestration (ARI, WebSocket, outbound campaigns) as alternative path.
6. **Bifrost auth**: LiteLLM v1.82.6 stores tokens in `LiteLLM_VerificationToken` (sha256 hash, no salt column in this version). Master key must be manually seeded or auto-seeded on fresh DB. `${VAR}` not supported in config.yaml — use `os.environ/VAR` syntax.

---
(pending commit — bifrost auth + config fix, kokoro compose entry, env var defaults)
```
