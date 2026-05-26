# AIOS — Complete Resource Inventory
## Single source of truth for every service, port, credential, and dependency

---

## 1. SERVICES — All 34 Compose Services (33 containers running)

### DMZ Zone — 10.10.0.0/24
| Service | Container | Image | IP | Ports | Status | Endpoint |
|---------|-----------|-------|----|-------|--------|----------|
| Traefik | aios-traefik | traefik:latest | 10.10.0.10 | 80, 443 | ✅ healthy | admin.socialbeesai.com |
| CrowdSec | aios-crowdsec | crowdsecurity/crowdsec:latest | 10.10.0.11 | 8080 | ✅ healthy | (internal — API only) |

### App Zone — 10.20.0.0/24
| Service | Container | Image | IP | Ports | Status | Endpoint |
|---------|-----------|-------|----|-------|--------|----------|
| Keycloak | aios-keycloak | quay.io/keycloak/keycloak:26.1 | 10.20.0.40 | 8080 | ✅ running | keycloak.socialbeesai.com |
| GitOps | aios-gitops | alpine:latest | 10.20.0.100 | — | ✅ healthy | (internal — polls GitHub) |
| Hermes | aios-hermes | alpine:latest | 10.20.0.70 | — | ✅ healthy | (internal — 24/7 ops) |
| n8n | aios-n8n | n8nio/n8n:latest | 10.20.0.10 | 5678 | ✅ healthy | n8n.socialbeesai.com |
| n8n-db | aios-n8n-db | postgres:16-alpine | 10.20.0.15 | 5432 | ✅ healthy | (internal) |
| n8n-worker-1 | aios-n8n-worker-1 | n8nio/n8n:latest | 10.20.0.13 | — | ✅ running | concurrency=10 |
| n8n-worker-2 | aios-n8n-worker-2 | n8nio/n8n:latest | 10.20.0.12 | — | ✅ running | concurrency=10 |

### Data Zone — 10.30.0.0/24 (internal:true — NO internet access)
| Service | Container | Image | IP | Ports | Status | Endpoint |
|---------|-----------|-------|----|-------|--------|----------|
| PostgreSQL | aios-postgres | pgvector/pgvector:0.8.0-pg16 | 10.30.0.10 | 5432 | ✅ healthy | (internal) |
| Qdrant | aios-qdrant | qdrant/qdrant:latest | 10.30.0.20 | 6333, 6334 | ✅ healthy | qdrant.socialbeesai.com/dashboard |
| Redis | aios-redis | redis:7-alpine | 10.30.0.30 | 6379 | ✅ healthy | (internal — n8n queue + cache) |
| MinIO | aios-minio | minio/minio:latest | 10.30.0.40 | 9000, 9001 | ✅ healthy | data.socialbeesai.com/minio |

### AI Zone — 10.40.0.0/24
| Service | Container | Image | IP | Ports | Status | Endpoint |
|---------|-----------|-------|----|-------|--------|----------|
| Bifrost (LiteLLM) | aios-bifrost | ghcr.io/berriai/litellm:main-latest | 10.40.0.10 | 4000 | ✅ healthy | ai.socialbeesai.com |
| Ollama | aios-ollama | ollama/ollama:latest | 10.40.0.20 | 11434 | ✅ healthy | (internal — embeddings + vision) |
| Chatterbox TTS | aios-chatterbox | travisvn/chatterbox-tts-api:latest | 10.40.0.30 | 4123 | ✅ running | (internal — GPU TTS) |
| Frigate NVR | aios-frigate | ghcr.io/blakeblackshear/frigate:stable | 10.40.0.50 | 5000 | ✅ healthy | frigate.socialbeesai.com |

### Voice Zone — 10.50.0.0/24
| Service | Container | Image | IP | Ports | Status | Endpoint |
|---------|-----------|-------|----|-------|--------|----------|
| Mosquitto MQTT | aios-mosquitto | eclipse-mosquitto:latest | 10.50.0.20 | 1883, 9001 | ✅ running | (internal — event bus) |
| Dograh API | aios-dograh-api | dograhai/dograh-api:latest | 10.50.0.30 | 8080 | ✅ running | (internal) |
| Dograh UI | aios-dograh-ui | dograhai/dograh-ui:latest | 10.50.0.31 | 3010 | ✅ running | voice.socialbeesai.com |

### Monitoring Zone — 10.60.0.0/24
| Service | Container | Image | IP | Ports | Status | Endpoint |
|---------|-----------|-------|----|-------|--------|----------|
| Langfuse | aios-langfuse | langfuse/langfuse:latest | 10.60.0.10 | 3000 | ✅ live | langfuse.socialbeesai.com |
| ClickHouse | aios-clickhouse | clickhouse/clickhouse-server:latest | 10.60.0.11 | 8123, 9000 | ✅ healthy | clickhouse.socialbeesai.com |
| Prometheus | aios-prometheus | prom/prometheus:latest | 10.60.0.20 | 9090 | ✅ running | monitor.socialbeesai.com/prometheus |
| Grafana | aios-grafana | grafana/grafana:latest | 10.60.0.30 | 3000 | ✅ running | monitor.socialbeesai.com/grafana |
| Loki | aios-loki | grafana/loki:latest | 10.60.0.40 | 3100 | ✅ running | (internal — logs) |
| Portainer | aios-portainer | portainer/portainer-ce:latest | 10.60.0.50 | 9000 | ✅ running | monitor.socialbeesai.com/portainer |
| cAdvisor | aios-cadvisor | gcr.io/cadvisor/cadvisor:latest | 10.60.0.60 | 8080 | ✅ running | monitor.socialbeesai.com/cadvisor |
| Node Exporter | aios-node-exporter | prom/node-exporter:latest | 10.60.0.61 | 9100 | ✅ running | (internal — host metrics) |
| Dashy | aios-dashy | lissy93/dashy:latest | 10.60.0.70 | 80 | ✅ live | socialbeesai.com |

### Host Network Mode — 10.0.0.100
| Service | Container | Image | IP | Ports | Status | Endpoint |
|---------|-----------|-------|----|-------|--------|----------|
| Vault | aios-vault | hashicorp/vault:latest | 10.0.0.100 | 8200 | ✅ unsealed | vault.socialbeesai.com |
| Vault Unseal | aios-vault-unseal | hashicorp/vault:latest | 10.0.0.100 | — | ✅ (one-shot init) | (internal) |
| Asterisk | aios-asterisk | aios-asterisk:latest (source build) | 10.0.0.100 | 5060/udp, 5061/tcp, 8088, 10000-20000/udp | ✅ healthy | (internal — SIP PBX) |
| DNSmasq-TFTP | aios-dnsmasq-tftp | andyshinn/dnsmasq | 10.0.0.100 | 69/udp | ✅ running | (internal — Cisco phone provisioning) |

### NOT DEPLOYED (no container, route returns 502)
| Service | Endpoint | Action Needed |
|---------|----------|---------------|
| WireGuard VPN | vpn.socialbeesai.com | Add compose service + route |
| Open WebUI | chat.socialbeesai.com | Add compose service + image |
| Flowise | app.socialbeesai.com/flowise | Already in compose — `docker compose up -d flowise` |
| Supabase | (none) | Only Postgres running, no Supabase Studio |

---

## 2. DOCKER NETWORKS

| Network | Subnet | Internal | Used By |
|---------|--------|----------|---------|
| aios-dmz | 10.10.0.0/24 | no | Traefik, CrowdSec, Portainer (secondary) |
| aios-app | 10.20.0.0/24 | no | n8n, n8n-db, n8n-workers, Keycloak, GitOps, Hermes |
| aios-data | 10.30.0.0/24 | **yes** | PostgreSQL, Qdrant, Redis, MinIO, Langfuse (secondary), Bifrost (secondary) |
| aios-ai | 10.40.0.0/24 | no | Bifrost, Ollama, Chatterbox, Frigate |
| aios-voice | 10.50.0.0/24 | no | Mosquitto, Dograh API, Dograh UI, Chatterbox (secondary) |
| aios-mon | 10.60.0.0/24 | no | Langfuse, ClickHouse, Prometheus, Grafana, Loki, Portainer, cAdvisor, Node Exporter, Dashy |
| aios-foss | 10.70.0.0/24 | no | (reserved for ERPNext, Odoo, Twenty CRM) |

---

## 3. VOLUMES

| Volume | Mount | Service |
|--------|-------|---------|
| postgres-data | /var/lib/postgresql/data | PostgreSQL |
| qdrant-data | /qdrant/storage | Qdrant |
| minio-data | /data | MinIO |
| crowdsec-data | /var/lib/crowdsec/data | CrowdSec |
| vault-data | /vault/file | Vault (bind mount: /aios/data/vault) |
| asterisk-data | /var/lib/asterisk | Asterisk |
| asterisk-log | /var/log/asterisk | Asterisk |
| mosquitto-data | /mosquitto/data | Mosquitto |
| mosquitto-log | /mosquitto/log | Mosquitto |
| clickhouse-data | /var/lib/clickhouse | ClickHouse |
| ollama-data | /root/.ollama | Ollama |
| n8n-data | /home/node/.n8n | n8n |
| n8n-db | /var/lib/postgresql/data | n8n PostgreSQL |
| prometheus-data | /prometheus | Prometheus |
| portainer-data | /data | Portainer |
| frigate-data | /media/frigate | Frigate |
| chatterbox-data | /app/data | Chatterbox TTS |
| chatterbox-voices | /app/voices | Chatterbox TTS |
| chatterbox-output | /app/output | Chatterbox TTS |

---

## 4. CREDENTIALS REFERENCE

| Service | Credential | Location | Value |
|---------|-----------|----------|-------|
| Server SSH | user/pass | `.env` | ai / Lahore*999 |
| PostgreSQL | user/pass | `.env` | aios / aios_secret_2026 |
| MinIO Console | user/pass | `.env` | admin / minioadmin |
| Grafana | user/pass | `.env` | admin / grafana_admin_2026 |
| Keycloak | user/pass | `.env` | admin / admin |
| Vault | root token | `.vault-keys` | (see .vault-keys on server) |
| Vault | unseal keys×5 | `.vault-keys` | (5 keys in .vault-keys) |
| Qdrant | API key | `.env` | aios_qdrant_2026 |
| Bifrost | admin key | `.env` | sk-aios-master-admin-key-change-me |
| n8n | DB password | `.env` | 21e8c7e99182e353a7326dff9b40d4ec |
| n8n | encryption key | `.env` | c9f0d2291d788460e5fc00a29763a0b3e9b8e90d29260cee19ba4cafb7c0b423 |
| Dograh | JWT secret | `.env` | aios-dograh-jwt-secret-2026 |
| Asterisk ARI | user/pass | `.env` | ai / 95vt3r6ke1w8lgqg6qpcui8e |
| Ext 100–104,9000 | SIP secrets | `.env` | (per-extension, in .env) |
| OpenRouter | API key | `.env` | sk-or-v1-placeholder (NEEDS REAL KEY) |
| Cloudflare | API key | `.env` | (see .env on server) |
| CrowdSec | API key | `.env` | (see .env on server) |
| Frigate RTSP | password | `.env` | Lahore*999 (same as server) |

Full list: `/aios/scripts/creds.sh` (redacted for git — secrets reference ".env on server")

---

## 5. CONFIG FILES

### Traefik (`/aios/configs/traefik/`)
| File | Purpose |
|------|---------|
| `traefik.yml` | Static config — providers, entrypoints, certresolver |
| `dynamic/aios.yml` | 16 routers + middlewares + services (all zones) |

### Asterisk (`/aios/configs/asterisk/`)
| File | Purpose |
|------|---------|
| `Dockerfile.asterisk` | Source compile v22.9.0 |
| `docker-entrypoint.sh` | envsubst at runtime |
| `pjsip.conf` | 6 endpoints + templates |
| `ari.conf` | ARI API user |
| `extensions.conf` | Dialplan |
| `asterisk.conf` | Directories + options |
| `http.conf` | HTTP/ARI server |
| `modules.conf` | Module autoload |
| `rtp.conf` | RTP port range 10000-20000 |
| `logger.conf` | Logging config |
| `voicemail.conf` | Voicemail |
| `ai-agent.agi` | AI bridge script (TODO) |

### DNSmasq-TFTP (`/aios/configs/dnsmasq/`)
| File | Purpose |
|------|---------|
| `SEP00270DC01C92.cnf.xml` | Cisco 7962 phone SEP config |
| `XMLDefault.cnf.xml` | Default phone config |
| `dialplan.xml` | Phone dial plan |
| `g3-tones.xml` | Tone definitions |
| `dnsmasq-tftp.conf` | TFTP-only server config |

### Bifrost (`/aios/configs/bifrost/`)
| File | Purpose |
|------|---------|
| `config.yaml` | LiteLLM gateway — Ollama (local) + OpenRouter routes |

### Other Configs
| Path | Contents |
|------|----------|
| `/aios/configs/crowdsec/` | WAF acquisition + parser configs |
| `/aios/configs/clickhouse/` | cluster.xml + keeper.xml |
| `/aios/configs/mosquitto/` | mosquitto.conf |
| `/aios/configs/grafana/` | grafana.ini, dashboards/ |
| `/aios/configs/prometheus/` | prometheus.yml, scrape configs |

---

## 6. KEY DIRECTORIES

| Path | Purpose | Git? |
|------|---------|------|
| `/aios/` | Project root | ✅ |
| `/aios/docs/` | Architecture, SOPs, security, checkpoint | ✅ |
| `/aios/configs/` | Service configurations | ✅ |
| `/aios/scripts/` | Automation tools (creds, test, diagnose, verify) | ✅ |
| `/aios/ansible/` | Server setup playbooks | ✅ |
| `/aios/data/` | Runtime data (volumes, bind mounts) | ❌ (.gitignore) |
| `/aios/.env` | Environment secrets | ❌ (.gitignore) |
| `/aios/.vault-keys` | Vault unseal keys + root token | ❌ (.gitignore) |
| `/aios/n8n/workflows/` | Use-case workflows | ✅ |
| `/aios/n8n/internal/` | Lab/internal workflows | ✅ |
| `/aios/langfuse/prompts/` | Agent system prompts (versioned) | ✅ |

---

## 7. SERVICE DEPENDENCIES — v1 Architecture

```
LLM ROUTING (v1 — Direct OpenRouter, Bifrost as optional gateway)
  n8n → OpenRouter API → Langfuse log (planned)
  Bifrost → Ollama (local inference, embeddings)
  Bifrost → OpenRouter (cloud models, fallback)

GPU (Quadro M4000 8GB — no LLM inference, only utilities)
  Ollama → nomic-embed-text (embeddings → Qdrant)
  Ollama → LLaVA (image/OCR for Frigate)
  Chatterbox → TTS (voice cloning for Dograh)
  Frigate → GPU-accelerated object detection

VOICE PIPELINE
  Caller → SIP Trunk → Asterisk → Dograh
    → Whisper STT (CPU — not GPU)
    → LLM response (via n8n → OpenRouter)
    → Chatterbox TTS (local GPU)
  → Audio back → Asterisk → Caller

SURVEILLANCE PIPELINE
  IP Camera → RTSP → Frigate NVR
    → GPU object detection (person, vehicle, animal)
    → MQTT events → n8n workflow
    → WhatsApp alert (via OpenRouter/API)

DATA LAYER
  PostgreSQL — agent memory, conversation history (pgvector)
  Qdrant — RAG overflow, temp/volatile data
  Redis — n8n queue, session cache
  MinIO — client docs, recordings, backups
  Langfuse — LLM observability, logging, cost tracking
```

---

## 8. OLLAMA MODELS

| Model | Size | Purpose | Status |
|-------|------|---------|--------|
| nomic-embed-text | ~500MB | Embeddings for Qdrant | ✅ Kept |
| llava:latest | 7B (~4.5GB) | Vision/OCR | ✅ Kept |

All other LLM models removed — use OpenRouter free tier for inference.

---

*Created May 21, 2026 • Updated May 26, 2026 — AIOS Inventory v4.2*
