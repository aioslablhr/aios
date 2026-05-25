# AIOS — Complete Resource Inventory
## Single source of truth for every service, port, credential, and dependency

---

## 1. SERVICES

| Service | Container | Image | Zone | IP | Ports | Status | Notes |
|---------|-----------|-------|------|----|-------|--------|-------|
| PostgreSQL | aios-postgres | postgres:16-alpine | data | 10.30.0.10 | 5432 | ✅ healthy | |
| Qdrant | aios-qdrant | qdrant/qdrant:latest | data | 10.30.0.20 | 6333, 6334 | ✅ healthy | RAG fallback for overflow |
| Redis | aios-redis | redis:7-alpine | data | 10.30.0.30 | 6379 | ✅ healthy | n8n queue, cache — in compose |
| MinIO | aios-minio | minio/minio:latest | data | 10.30.0.40 | 9000, 9001 | ✅ running | S3 storage, events bucket |
| Langfuse | aios-langfuse | langfuse/langfuse:latest | data+mon | 10.30.0.50, 10.60.0.10 | 3000 | ✅ live | LLM observability |
| ClickHouse | aios-clickhouse | clickhouse/clickhouse-server:latest | mon | 10.60.0.11 | 8123, 9000 | ✅ healthy | Langfuse trace storage |
| Bifrost | aios-bifrost | ghcr.io/berriai/litellm:main-latest | ai+data | 10.40.0.10 | 4000 | ✅ healthy | v2+ — not needed for v1 inference |
| Ollama | aios-ollama | ollama/ollama:latest | ai | 10.40.0.20 | 11434 | ✅ healthy | Embeddings + vision only |
| Vault | aios-vault | hashicorp/vault:latest | app | 10.20.0.50 | 8200 | ✅ unsealed | Move from host net (TODO) |
| Keycloak | aios-keycloak | quay.io/keycloak/keycloak:26.1 | app | 10.20.0.40 | 8080 | ✅ healthy | SSO, multi-tenant |
| Traefik | aios-traefik | traefik:v3.3 | dmz | 10.10.0.10 | 80, 443 | ✅ healthy | Reverse proxy |
| CrowdSec | aios-crowdsec | crowdsecurity/crowdsec:latest | dmz | 10.10.0.11 | 8080 | ✅ healthy | WAF |
| Dashy | aios-dashy | lissy93/dashy:latest | mon | 10.60.0.70 | 80 | ✅ live | Navigation |
| GitOps | aios-gitops | alpine:latest | app | 10.20.0.100 | — | ✅ healthy | Auto-deploy |
| Hermes | aios-hermes | alpine:latest | app | 10.20.0.70 | — | ✅ healthy | Ops agent |
| DNSmasq-TFTP | aios-dnsmasq-tftp | andyshinn/dnsmasq | host | 10.0.0.100 | 69/udp | ✅ running | Cisco phone provisioning |
| Asterisk | aios-asterisk | aios-asterisk:latest (source) | host | 10.0.0.100 | 5060/udp, 5061/tcp, 8088, 10000-20000/udp | ✅ healthy | SIP trunking |
| WireGuard | aios-wireguard | lscr.io/linuxserver/wireguard:latest | app | 10.20.0.90 | 51820/udp | ⬜ TODO | VPN for remote access |
| Dograh | aios-dograh | dograh/dograh:latest | voice | 10.50.0.30 | 3000 | ⬜ TODO | Voice agent orchestration |
| Chatterbox | aios-chatterbox | chatterbox/chatterbox:latest | ai | 10.40.0.30 | 8000 | ⬜ TODO | TTS/voice cloning (GPU) |
| n8n | aios-n8n | n8nio/n8n:latest | app | 10.20.0.10 | 5678 | ✅ healthy | Workflow orchestration — active, queue mode |
| n8n-db | aios-n8n-db | postgres:16-alpine | app | 10.20.0.15 | 5432 | ✅ healthy | n8n dedicated PostgreSQL |
| n8n-worker-1 | aios-n8n-worker-1 | n8nio/n8n:latest | app+data | 10.20.0.13 | — | ✅ running | Stateless worker (concurrency=10) |
| n8n-worker-2 | aios-n8n-worker-2 | n8nio/n8n:latest | app+data | 10.20.0.12 | — | ✅ running | Stateless worker (concurrency=10) |
| Redis | aios-redis | redis:7-alpine | data | 10.30.0.30 | 6379 | ✅ healthy | n8n queue, cache — in compose now |
| Flowise | aios-flowise | flowiseai/flowise:latest | app | 10.20.0.20 | 3000 | ⬜ TODO | Visual agent builder |
| Prometheus | aios-prometheus | prom/prometheus:latest | mon | 10.60.0.20 | 9090 | ⬜ TODO | Metrics |
| Grafana | aios-grafana | grafana/grafana:latest | mon | 10.60.0.30 | 3000 | ⬜ TODO | Dashboards |

---

## 2. DOCKER NETWORKS

| Network | Subnet | Internal | Used By |
|---------|--------|----------|---------|
| aios-dmz | 10.10.0.0/24 | no | Traefik, CrowdSec |
| aios-app | 10.20.0.0/24 | no | Vault, Keycloak, n8n, workers, Flowise, WireGuard, GitOps, Hermes |
| aios-data | 10.30.0.0/24 | **yes** | PostgreSQL, Qdrant, Redis, MinIO, Langfuse |
| aios-ai | 10.40.0.0/24 | no | Bifrost, Ollama, Chatterbox |
| aios-voice | 10.50.0.0/24 | no | Asterisk (host net), Dograh, MQTT |
| aios-mon | 10.60.0.0/24 | no | Langfuse, ClickHouse, Prometheus, Grafana, Dashy |
| aios-foss | 10.70.0.0/24 | no | ERPNext, Odoo, Twenty CRM (future) |

---

## 3. VOLUMES

| Volume | Mount | Service |
|--------|-------|---------|
| postgres-data | — | PostgreSQL |
| qdrant-data | — | Qdrant |
| minio-data | — | MinIO |
| crowdsec-data | — | CrowdSec |
| vault-data | — | Vault (unused — bind mount used instead) |
| asterisk-data | — | Asterisk |
| asterisk-log | — | Asterisk |
| mosquitto-data | — | MQTT (future) |
| mosquitto-log | — | MQTT (future) |
| clickhouse-data | — | ClickHouse |
| ollama-data | — | Ollama (model storage) |
| n8n-data | — | n8n (config, cache) |
| n8n-db | — | n8n PostgreSQL data |
| Bind: /aios/data/vault | /vault/file | Vault (raft storage) |

---

## 4. CREDENTIALS

| Credential | Location | Type | Notes |
|------------|----------|------|-------|
| Server sudo | `.env` → `SERVER_PASS` | plaintext | chmod 600 |
| PostgreSQL root | `.env` → `POSTGRES_PASSWORD` | plaintext | `aios_secret_2026` |
| Cloudflare API | `.env` → `CLOUDFLARE_API_KEY` | plaintext | DNS:Edit scope |
| CrowdSec API | `.env` → `CROWDSEC_API_KEY` | plaintext | — |
| Langfuse NextAuth | `.env` → `LANGFUSE_NEXTAUTH_SECRET` | plaintext | Generated random hex |
| Langfuse Salt | `.env` → `LANGFUSE_SALT` | plaintext | Generated random hex |
| Qdrant API | `.env` → `QDRANT_API_KEY` | plaintext | Not yet enforced |
| OpenRouter API | `.env` → `OPENROUTER_API_KEY` | plaintext | `sk-or-v1-3924a91d...` — free tier, rate-limited |
| n8n DB password | `.env` → `N8N_DB_PASSWORD` | plaintext | Generated, injected into n8n + workers |
| n8n encryption key | `.env` → `N8N_ENCRYPTION_KEY` | plaintext | Generated, 32-char hex |
| Ext 100-104, 9000 | `.env` → `EXT_xxx_SECRET` | plaintext | Injected via envsubst |
| ARI admin | `.env` → `ARI_ADMIN_PASSWORD` | plaintext | Injected via envsubst |
| Vault root token | `.vault-keys` | plaintext | chmod 600, NOT in git |
| Vault unseal keys | `.vault-keys` | plaintext | chmod 600, NOT in git |

---

## 5. CONFIG FILES

### Bifrost (`/aios/configs/bifrost/`)
| File | Purpose | Status |
|------|---------|--------|
| `config.yaml` | LiteLLM gateway — 6 models (Ollama + OpenRouter) | ⚠️ Needs rewrite: remove local LLMs, keep only OpenRouter routes |

### ClickHouse (`/aios/configs/clickhouse/`)
| File | Purpose |
|------|---------|
| `cluster.xml` | Single-node cluster definition |
| `keeper.xml` | Embedded Keeper config (replaces ZooKeeper) |

### DNSmasq-TFTP (`/aios/configs/dnsmasq/`)
| File | Purpose |
|------|---------|
| `SEP00270DC01C92.cnf.xml` | Cisco 7962 phone SEP config |
| `XMLDefault.cnf.xml` | Default phone config |
| `dialplan.xml` | Phone dial plan |
| `g3-tones.xml` | Tone definitions |
| `dnsmasq-tftp.conf` | TFTP-only server config |
| `dnsmasq.conf` | Full DHCP+TFTP config (temp) |

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

### MQTT (`/aios/configs/mosquitto/`)
| File | Purpose |
|------|---------|
| `mosquitto.conf` | Listener 1883 + websockets 9001 |

---

## 6. KEY PATHS

| Path | Purpose | Git? |
|------|---------|------|
| `/aios/` | Project root | ✅ |
| `/aios/docs/` | Architecture, SOPs, security, checkpoint | ✅ |
| `/aios/configs/` | Service configurations | ✅ |
| `/aios/scripts/` | Automation tools | ✅ |
| `/aios/ansible/` | Server setup playbooks | ✅ |
| `/aios/data/` | Runtime data (volumes, bind mounts) | ❌ (.gitignore) |
| `/aios/.env` | Environment secrets | ❌ (.gitignore) |
| `/aios/.vault-keys` | Vault unseal keys + root token | ❌ (.gitignore) |
| `/aios/wiki/` | LLM Wiki — compiled knowledge base | ✅ |
| `/aios/obsidian/` | Raw source vault for wiki compilation | ❌ |
| `/aios/clients/` | Per-client configs + knowledge docs | ✅ |
| `/aios/n8n/workflow-templates/` | Capability + use case templates | ✅ |
| `/aios/langfuse/prompts/` | Agent system prompts (versioned) | ✅ |

---

## 7. SERVICE DEPENDENCIES — v1 Architecture

```
INFERENCE (v1 — Direct OpenRouter, no Bifrost)
  n8n → OpenRouter API → Langfuse log

GPU (Quadro M4000 — no LLMs, only utilities)
  Ollama → nomic-embed-text (embeddings → Qdrant)
  Ollama → LLaVA (image/OCR)
  Whisper → Dograh (STT for voice)
  Chatterbox → Dograh (TTS for voice)

VOICE PIPELINE
  Caller → SIP Trunk → Asterisk → Dograh
    → Whisper STT (local GPU)
    → n8n → OpenRouter → LLM response
    → Chatterbox TTS (local GPU)
  → Audio back → Asterisk → Caller

KNOWLEDGE (LLM Wiki pattern — Karpathy April 2026)
  Obsidian vault (raw .md sources)
    → LLM compiles at ingest time
    → wiki/ folder (structured, cross-referenced)
    → Agent reads wiki at query time
    → Qdrant RAG as fallback for overflow/volatile data

DATA LAYER
  PostgreSQL — agent memory, conversation history
  Qdrant — RAG overflow, temp/volatile data
  Redis — n8n queue, session cache
  MinIO — client docs, recordings, backups
  Langfuse — LLM observability, logging
```

---

## 8. OLLAMA MODELS (v1 — Keep only utility models)

| Model | Size | Purpose | Keep? |
|-------|------|---------|-------|
| mistral:latest | 7.2B | ~5GB | ❌ Remove (use OpenRouter free tier) |
| qwen2.5:latest | 7.6B | ~5GB | ❌ Remove (use OpenRouter free tier) |
| llama3.2:latest | 3.2B | ~2GB | ❌ Remove (not useful) |
| llama3.1:8b | 8.0B | ~4.9GB | ❌ Remove (use OpenRouter free tier) |
| nomic-embed-text | — | <500MB | ✅ Keep (embeddings) |
| llava:latest | 7B | ~4.5GB | ✅ Keep (vision/OCR) |

---

*Created May 21, 2026 • Updated May 26, 2026 — AIOS Inventory v1 MVP*
