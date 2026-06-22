# AIOS — Complete Resource Inventory
## Single source of truth for every service, port, credential, and dependency
## Last verified: June 22, 2026 — all 48 containers inspected

---

## 1. SERVICES — All 48 Containers Running

### DMZ Zone — 10.10.0.0/24
| Service | Container | Image | IP | Ports | Status | Endpoint |
|---------|-----------|-------|----|-------|--------|----------|
| Traefik | aios-traefik | traefik:latest | 10.10.0.10 | 80, 443 | healthy | admin.socialbeesai.com |
| CrowdSec | aios-crowdsec | crowdsecurity/crowdsec:latest | 10.10.0.11 | 8080 | crash-loop | (internal — WAF API, YAML bug) |

### App Zone — 10.20.0.0/24
| Service | Container | Image | IP | Ports | Status | Endpoint |
|---------|-----------|-------|----|-------|--------|----------|
| Keycloak | aios-keycloak | quay.io/keycloak/keycloak:26.1 | 10.20.0.40 | 8080 | running (health starting) | keycloak.socialbeesai.com |
| n8n | aios-n8n | n8nio/n8n:latest | 10.20.0.10 | 5678 | running | n8n.socialbeesai.com |
| n8n-db | aios-n8n-db | postgres:16-alpine | 10.20.0.15 | 5432 | healthy | (internal) |
| n8n-worker-1 | aios-n8n-worker-1 | n8nio/n8n:latest | 10.20.0.13 | — | running | concurrency=10 |
| n8n-worker-2 | aios-n8n-worker-2 | n8nio/n8n:latest | 10.20.0.12 | — | running | concurrency=10 |
| Flowise | aios-flowise | flowiseai/flowise:latest | 10.20.0.20 | 3000 | running | app.socialbeesai.com/flowise |
| MCP Server | aios-mcp | mcp-server:latest (custom) | 10.20.0.30 | 8000 | running | mcp.socialbeesai.com |
| GitOps | aios-gitops | alpine:latest | 10.20.0.100 | — | crash-loop | (internal — polls GitHub, keeps dying) |
| Hermes | aios-hermes | alpine:latest | 10.20.0.70 | — | running | (internal — 24/7 ops) |

### Data Zone — 10.30.0.0/24 (internal:true — NO internet access)
| Service | Container | Image | IP | Ports | Status | Endpoint |
|---------|-----------|-------|----|-------|--------|----------|
| PostgreSQL | aios-postgres | pgvector/pgvector:0.8.0-pg16 | 10.30.0.10 | 5432 | healthy | (internal) |
| Qdrant | aios-qdrant | qdrant/qdrant:latest | 10.30.0.20 | 6333, 6334 | healthy | qdrant.socialbeesai.com/dashboard |
| Redis | aios-redis | redis:7-alpine | 10.30.0.30 | 6379 | healthy | (internal — n8n queue + cache) |
| MinIO | aios-minio | minio/minio:latest | 10.30.0.40 | 9000, 9001 | unhealthy | data.socialbeesai.com/minio |

### AI Zone — 10.40.0.0/24
| Service | Container | Image | IP | Ports | Status | Endpoint |
|---------|-----------|-------|----|-------|--------|----------|
| Bifrost (LiteLLM) | aios-bifrost | ghcr.io/berriai/litellm:main-latest | 10.40.0.10 | 4000 | healthy | ai.socialbeesai.com |
| Ollama | aios-ollama | ollama/ollama:latest | 10.40.0.20 | 11434 | healthy | (internal — CPU embeddings + vision) |
| Chatterbox TTS | aios-chatterbox | travisvn/chatterbox-tts-api:latest | 10.40.0.30 | 4123 | running (healthy) | (internal — GPU 4GB VRAM, UNUSED by Dograh) |
| Kokoro TTS | aios-kokoro | ghcr.io/remsky/kokoro-fastapi-cpu:latest | 10.40.0.31 | 8880 | running | (internal — CPU TTS, UNUSED by Dograh) |
| XTTS Urdu | aios-xtts-urdu | aios-xtts-urdu:latest (custom) | 10.40.0.32 | 8020 (127.0.0.1) | running | (internal — Urdu TTS, CPU forced, voice cloned) |
| TTS Router | aios-tts-router | aios-tts-router:latest (custom) | 10.40.0.33 | 8030 (127.0.0.1) | running | (internal — cloud-only: UpliftAI/ElevenLabs/Google) |
| Dia-1.6B-Urdu | aios-dia-tts | aios-dia-tts:latest (custom) | 10.40.0.34 | 8034 (127.0.0.1) | running but BROKEN | (GPU Urdu TTS — model fails to load, Pydantic bug) |
| Open WebUI | aios-open-webui | ghcr.io/open-webui/open-webui:main | 10.40.0.35 | 3011:8080 | running | chat.socialbeesai.com |
| Whisper STT | aios-whisper-stt | onerahmet/openai-whisper-asr-webservice:latest | 10.40.0.40 | 9000 (127.0.0.1:8140) | running | (internal — ZOMBIE, not used by any workflow) |
| Speaches STT/TTS | aios-speaches | ghcr.io/speaches-ai/speaches:latest-cpu | 10.40.0.41 | 8000 (127.0.0.1:8141) | healthy | (internal — faster-whisper-large-v3, UNUSED) |
| Docling | aios-docling | aios-docling:latest (custom) | 10.40.0.42 | — | healthy | (internal — document parsing) |
| Mem0 | aios-mem0 | aios-mem0:latest (custom) | 10.40.0.43 | — | healthy | (internal — memory layer) |
| Frigate NVR | aios-frigate | ghcr.io/blakeblackshear/frigate:stable | 10.40.0.50 | 5000 | healthy | frigate.socialbeesai.com |

### Voice Zone — 10.50.0.0/24
| Service | Container | Image | IP | Ports | Status | Endpoint |
|---------|-----------|-------|----|-------|--------|----------|
| Mosquitto MQTT | aios-mosquitto | eclipse-mosquitto:latest | 10.50.0.20 | 1883, 9001 | running | (internal — event bus) |
| Dograh API | aios-dograh-api | ghcr.io/dograh-hq/dograh-api:latest | 10.50.0.30 | 8000 | healthy | (internal — v1.35.0, OSS GHCR) |
| Dograh UI | aios-dograh-ui | ghcr.io/dograh-hq/dograh-ui:latest | 10.50.0.31 | 3010 | running | voice.socialbeesai.com |

### Monitoring Zone — 10.60.0.0/24
| Service | Container | Image | IP | Ports | Status | Endpoint |
|---------|-----------|-------|----|-------|--------|----------|
| Langfuse | aios-langfuse | langfuse/langfuse:latest | 10.60.0.10 | 3000 | running | langfuse.socialbeesai.com |
| ClickHouse | aios-clickhouse | clickhouse/clickhouse-server:latest | 10.60.0.11 | 8123, 9000 | healthy | clickhouse.socialbeesai.com |
| Prometheus | aios-prometheus | prom/prometheus:latest | 10.60.0.20 | 9090 | running | prometheus.socialbeesai.com |
| Grafana | aios-grafana | grafana/grafana:latest | 10.60.0.30 | 3000 | running | grafana.socialbeesai.com |
| Loki | aios-loki | grafana/loki:latest | 10.60.0.40 | 3100 | running | (internal — logs) |
| Portainer | aios-portainer | portainer/portainer-ce:latest | 10.60.0.50 | 9000 | running | portainer.socialbeesai.com, host:9000 |
| cAdvisor | aios-cadvisor | gcr.io/cadvisor/cadvisor:latest | 10.60.0.60 | 8080 | healthy | cadvisor.socialbeesai.com |
| Node Exporter | aios-node-exporter | prom/node-exporter:latest | 10.60.0.61 | 9100 | running | (internal — host metrics) |
| Dashy | aios-dashy | lissy93/dashy:latest | 10.60.0.70 | 8080 | running | socialbeesai.com |

### Host Network Mode — 10.0.0.100
| Service | Container | Image | IP | Ports | Status | Endpoint |
|---------|-----------|-------|----|-------|--------|----------|
| Vault | aios-vault | hashicorp/vault:latest | 10.0.0.100 | 8200 | unsealed | vault.socialbeesai.com |
| Vault Unseal | aios-vault-unseal | hashicorp/vault:latest | 10.0.0.100 | — | (one-shot init) | (internal) |
| Asterisk | aios-asterisk | aios-asterisk:latest (source build) | 10.0.0.100 | 5060/udp, 5061/tcp, 10000-20000/udp | healthy | (internal — SIP PBX 22.9.0) |
| DNSmasq-TFTP | aios-dnsmasq-tftp | andyshinn/dnsmasq | 10.0.0.100 | 69/udp | running | (internal — Cisco phone provisioning) |

### NOT DEPLOYED
| Service | Notes |
|---------|-------|
| WireGuard VPN | compose service not added |
| Supabase | only Postgres running, no Supabase Studio |

---

## 2. DOCKER NETWORKS

| Network | Subnet | Internal | Used By | Traefik On It? |
|---------|--------|----------|---------|----------------|
| aios-dmz | 10.10.0.0/24 | no | Traefik, CrowdSec | yes |
| aios-app | 10.20.0.0/24 | no | n8n, n8n-db, n8n-workers, Keycloak, Flowise, MCP, GitOps, Hermes | yes |
| aios-data | 10.30.0.0/24 | **yes** | PostgreSQL, Qdrant, Redis, MinIO, Langfuse (secondary), Bifrost (secondary) | yes |
| aios-ai | 10.40.0.0/24 | no | Bifrost, Ollama, Chatterbox, Kokoro, XTTS, TTS Router, DIA TTS, Speaches, Whisper, Frigate, Docling, Mem0 | yes |
| aios-voice | 10.50.0.0/24 | no | Mosquitto, Dograh API, Dograh UI, XTTS, TTS Router, DIA TTS, Speaches, Kokoro (secondary) | yes |
| aios-mon | 10.60.0.0/24 | no | Langfuse, ClickHouse, Prometheus, Grafana, Loki, Portainer, cAdvisor, Node Exporter, Dashy | yes |
| aios-foss | 10.70.0.0/24 | no | (reserved for ERPNext, Odoo, Twenty CRM) | NO — Traefik not on this net |

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
| dia-tts-cache | /app/model_cache | Dia-1.6B-Urdu TTS |
| speaches-cache | /home/ubuntu/.cache/huggingface/hub | Speaches STT/TTS |

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
| Vault | unseal keys x5 | `.vault-keys` | (5 keys in .vault-keys) |
| Qdrant | API key | `.env` | aios_qdrant_2026 |
| Bifrost | admin key | `.env` | sk-aios-master-admin-key-change-me |
| n8n | DB password | `.env` | 21e8c7e99182e353a7326dff9b40d4ec |
| n8n | encryption key | `.env` | c9f0d2291d788460e5fc00a29763a0b3e9b8e90d29260cee19ba4cafb7c0b423 |
| Dograh | JWT secret | `.env` | aios-dograh-jwt-secret-2026 |
| Asterisk ARI | user/pass | `.env` | ai / 95vt3r6ke1w8lgqg6qpcui8e |
| Ext 100-104, 9000 | SIP secrets | `.env` | (per-extension, in .env) |
| OpenRouter | API key | `.env` | sk-or-v1-0855e04fc... (REAL KEY — May 26) |
| Cloudflare | API key | `.env` | (see .env on server) |
| CrowdSec | API key | `.env` | (see .env on server) |
| Frigate RTSP | password | config.yml | Lahore999! |
| Flowise | user/pass | — | admin / admin |
| Portainer | host port | `.env` / compose | http://10.0.0.100:9000 (admin setup required) |
| AWS IAM | access keys | `/aios/aios_accessKeys.csv` | AKIA565H4TDW4RHSX7TJ |
| EC2 SSH | key pair | `/aios/aios-key.pem` | ubuntu@3.91.2.202 |

Full list: `docs/ref/credentials.md`

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
| `config.yaml` | LiteLLM gateway — 3 local Ollama + 25 OpenRouter $0 models (28 total) |

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
| `/aios/` | Project root | yes |
| `/aios/docs/` | Architecture, SOPs, security, checkpoint | yes |
| `/aios/configs/` | Service configurations | yes |
| `/aios/scripts/` | Automation tools (creds, test, diagnose, verify) | yes |
| `/aios/ansible/` | Server setup playbooks | yes |
| `/aios/data/` | Runtime data (volumes, bind mounts) | no (.gitignore) |
| `/aios/.env` | Environment secrets | no (.gitignore) |
| `/aios/.vault-keys` | Vault unseal keys + root token | no (.gitignore) |
| `/aios/n8n/workflows/` | Use-case workflows | yes |
| `/aios/n8n/internal/` | Lab/internal workflows | yes |
| `/aios/langfuse/prompts/` | Agent system prompts (versioned) | yes |

---

## 7. SERVICE DEPENDENCIES — v1 Architecture

```
LLM ROUTING (via Bifrost — 28 models)
  n8n → Bifrost (10.40.0.10:4000) → Ollama (local, free)
  n8n → Bifrost → OpenRouter $0 tier (25 free models)
  Bifrost failover: local → OpenRouter auto
  All logged to Langfuse for observability

GPU (Quadro M4000 8GB — no LLM inference, only utilities)
  Chatterbox → TTS GPU (4GB VRAM, unused by Dograh)
  Frigate → GPU-accelerated object detection (may use GPU if configured)
  Ollama → CPU only (models too large for remaining 4GB VRAM)
  XTTS Urdu → CPU only (CUDA_VISIBLE_DEVICES="" — VRAM contention)

VOICE PIPELINE (current — cloud-dependent)
  Caller → PJSIP → Asterisk → Stasis(dograh) → Dograh API (v1.35.0)
    → STT: Deepgram cloud (nova-3-general) — Speaches local unused
    → LLM: Speaches provider → Bifrost → OpenRouter (frontier-reasoning)
    → TTS: tts-router → UpliftAI/ElevenLabs cloud — Chatterbox/Kokoro/XTTS local unused
  → Audio back → Asterisk → Caller

  2 active agents: Ext 102 (Shin Travels), Ext 105 (Urdu)
  ARI connected: 1 active connection, app_name=dograh
  PJSIP endpoints: 7 defined, 2 registered (101=support trunk, 9000=Cisco phone)
  Calls processed: 5 total (lightly used)

SURVEILLANCE PIPELINE (active)
  IP Camera (10.0.0.51, Dahua IPC-B1E49-A-IL) → RTSP UDP → Frigate NVR
    → GPU object detection (person, vehicle, animal — CPU decoder, M4000 hwaccel unstable)
    → MQTT events → n8n workflow
    → WhatsApp alert (via Bifrost/OpenRouter)

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
| nomic-embed-text | 274MB | Embeddings for Qdrant | kept |
| qwen2.5:7b-instruct-q4_K_M | 4.7GB | General reasoning (local) | kept |
| llama3.2:3b-instruct-q4_K_M | 2.0GB | Lightweight chat (local) | kept |
| qalb-1.0-8b / alif-1.0-8b | 4.9GB each | Arabic/Urdu (local) | kept |
| llava:7b | 4.7GB | Vision/OCR | kept |

All LLM inference runs CPU-only (no VRAM available for LLM inference on Quadro M4000).
Main LLM path: Dograh → Bifrost → OpenRouter $0 tier.

---

## 9. BIFROST MODEL LIST (28 total)

### Local Ollama (3)
- mistral-7b, qwen-2.5-7b, llama-3-8b

### OpenRouter $0 Tier (25)
- openrouter-free, gemma-4-31b, gemma-4-26b, llama-70b, llama-3b
- deepseek-v4, qwen-coder, qwen-80b, hermes-405b, cobuddy
- owl-alpha, liquid-thinking, liquid-instruct, minimax-m2
- gpt-oss-120b, gpt-oss-20b, nemotron-reasoning, nemotron-nano-30b
- nemotron-120b, nemotron-vl, nemotron-9b, glm-4, dolphin-24b
- poolside-xs, poolside-m

---

## 10. AWS INFRASTRUCTURE

| Resource | ID/Value | Notes |
|----------|----------|-------|
| AWS Account | 959740418285 | IAM user: `aios` |
| Region | us-east-1 | Default VPC: vpc-07a4c322baf02e112 |
| EC2 Key Pair | aios-key | PEM at `/aios/aios-key.pem` on server |
| EC2 Instance | i-01b37e00dfe0fc251 | t3.micro, 3.91.2.202, us-east-1a |
| AMI | ami-0d7405d05f836d0d4 | Ubuntu 22.04 LTS |
| Docker | 29.5.3 + Compose v5.1.4 | Installed on EC2 |
| Security Group | sg-0c170aa450b71d1b0 | Ports 22, 80, 443, 5678 open |
| Subnet | subnet-0e4c29f19887dadf3 | Default, auto-assign public IP |
| Note | t3.micro (1GB RAM) too small for full AIOS stack | Upgrade to g4dn.xlarge needed |

---

## 11. KEY DIRECTORIES (Updated)

| Path | Purpose | Git? |
|------|---------|------|
| `/aios/configs/dia-tts/` | Dia-1.6B-Urdu TTS Docker build (Dockerfile.dia, server.py, requirements.txt) | yes |
| `/aios/configs/speaches/` | Speaches STT/TTS config (pre-built image, no local config needed) | no |

---

*Created May 21, 2026 • Updated June 18, 2026 — AIOS Inventory v7.0*
