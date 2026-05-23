# AIOS — Complete Resource Inventory
## Single source of truth for every service, port, credential, and dependency

---

## 1. SERVICES

| Service | Container | Image | Zone | IP | Ports | Status | Compose Line |
|---------|-----------|-------|------|----|-------|--------|-------------|
| PostgreSQL | aios-postgres | postgres:16-alpine | data | 10.30.0.10 | 5432 | ✅ healthy | 39 |
| Qdrant | aios-qdrant | qdrant/qdrant:latest | data | 10.30.0.20 | 6333, 6334 | ✅ healthy | 61 |
| Redis | aios-redis | redis:7-alpine | data | 10.30.0.30 | 6379 | ✅ healthy (orphan) | — |
| MinIO | aios-minio | minio/minio:latest | data | 10.30.0.40 | 9000, 9001 | ✅ healthy (orphan) | — |
| Langfuse | aios-langfuse | langfuse/langfuse:latest | data+mon | 10.30.0.50, 10.60.0.10 | 3000 | ✅ live | 112 |
| ClickHouse | aios-clickhouse | clickhouse/clickhouse-server:latest | mon | 10.60.0.11 | 8123, 9000 | ✅ healthy | 87 |
| Bifrost | aios-bifrost | ghcr.io/berriai/litellm:main-latest | ai+data | 10.40.0.10 | 4000 | ✅ healthy | 151 |
| Ollama | aios-ollama | ollama/ollama:latest | ai | 10.40.0.20 | 11434 | ✅ healthy | 177 |
| Vault | aios-vault | hashicorp/vault:latest | app (host) | 10.0.0.100 | 8200 | ✅ unsealed | 211 |
| Keycloak | aios-keycloak | quay.io/keycloak/keycloak:26.1 | app | 10.20.0.40 | 8080 | ✅ healthy (orphan) | — |
| Traefik | aios-traefik | traefik:v3.3 | dmz | 10.10.0.10 | 80, 443 | ✅ healthy (orphan) | — |
| CrowdSec | aios-crowdsec | crowdsecurity/crowdsec:latest | dmz | 10.10.0.11 | 8080 | ✅ healthy (orphan) | — |
| Dashy | aios-dashy | lissy93/dashy:latest | dmz | 10.60.0.70 | 80 | ✅ live (orphan) | — |
| GitOps | aios-gitops | alpine:latest | app | 10.20.0.100 | — | ✅ healthy | 288 |
| Hermes | aios-hermes | alpine:latest | app | 10.20.0.70 | — | ✅ healthy | 329 |
| DNSmasq-TFTP | aios-dnsmasq-tftp | andyshinn/dnsmasq | host | 10.0.0.100 | 69/udp | ✅ healthy | 384 |
| Asterisk | aios-asterisk | aios-asterisk:latest (source) | host | 10.0.0.100 | 5060/udp, 5061/tcp, 8088, 10000-20000/udp | ✅ healthy | 351 |

### Orphan Services (NOT in docker-compose)
Redis, MinIO, Keycloak, Traefik, CrowdSec, Dashy were deployed separately.
Need to be added to `docker-compose-aios.yml` or `docker-compose-apps.yml`.

---

## 2. DOCKER NETWORKS

| Network | Subnet | Internal | Used By |
|---------|--------|----------|---------|
| aios-dmz | 10.10.0.0/24 | no | Traefik, CrowdSec |
| aios-app | 10.20.0.0/24 | no | Vault (host net), Keycloak, GitOps, Hermes |
| aios-data | 10.30.0.0/24 | **yes** | PostgreSQL, Qdrant, Redis, MinIO, Langfuse |
| aios-ai | 10.40.0.0/24 | no | Bifrost, Ollama |
| aios-voice | 10.50.0.0/24 | no | Asterisk (host net), MQTT (future) |
| aios-mon | 10.60.0.0/24 | no | Langfuse, ClickHouse, Grafana (future), Dashy (future) |
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
| Bind: /aios/data/vault | /vault/file | Vault (raft storage) |

---

## 4. CREDENTIALS

| Credential | Location | Type | Notes |
|------------|----------|------|-------|
| Server sudo | `.env` → `SERVER_PASS` | plaintext | chmod 600 |
| PostgreSQL root | `.env` → `POSTGRES_PASSWORD` | plaintext | Shared across aios + langfuse + litellm DBs |
| Cloudflare API | `.env` → `CLOUDFLARE_API_KEY` | plaintext | DNS:Edit scope |
| CrowdSec API | `.env` → `CROWDSEC_API_KEY` | plaintext | — |
| Langfuse NextAuth | `.env` → `LANGFUSE_NEXTAUTH_SECRET` | plaintext | Generated random hex |
| Langfuse Salt | `.env` → `LANGFUSE_SALT` | plaintext | Generated random hex |
| Qdrant API | `.env` → `QDRANT_API_KEY` | plaintext | Not yet enforced |
| Bifrost Admin Key | `.env` → `BIFROST_ADMIN_KEY` (not in compose) | plaintext | Hardcoded in config.yaml: `sk-aios-master-admin-key-change-me` |
| OpenRouter API | `.env` → `OPENROUTER_API_KEY` | plaintext | **Placeholder** — `sk-or-v1-placeholder` |
| Ext 100 (Admin) | `.env` → `EXT_100_SECRET` | plaintext | Injected via envsubst |
| Ext 101 (Support) | `.env` → `EXT_101_SECRET` | plaintext | Injected via envsubst |
| Ext 102 (AI Agent) | `.env` → `EXT_102_SECRET` | plaintext | Injected via envsubst |
| Ext 103 (Test) | `.env` → `EXT_103_SECRET` | plaintext | Injected via envsubst |
| Ext 104 (Android) | `.env` → `EXT_104_SECRET` | plaintext | Injected via envsubst |
| Ext 9000 (Cisco) | `.env` → `EXT_9000_SECRET` | plaintext | Injected via envsubst |
| ARI admin | `.env` → `ARI_ADMIN_PASSWORD` | plaintext | Injected via envsubst |
| Vault root token | `.vault-keys` | plaintext | chmod 600, NOT in git |
| Vault unseal keys | `.vault-keys` | plaintext | chmod 600, NOT in git |
| Anthropic API | `.env` → (missing) | missing | Vault ready, migrate needed |
| OpenAI API | `.env` → (missing) | missing | Vault ready, migrate needed |

---

## 5. CONFIG FILES

### Bifrost (`/aios/configs/bifrost/`)
| File | Purpose | Credentials? |
|------|---------|-------------|
| `config.yaml` | LiteLLM gateway — 6 models, Ollama + OpenRouter, simple-shuffle routing | plaintext master key |

### ClickHouse (`/aios/configs/clickhouse/`)
| File | Purpose | Credentials? |
|------|---------|-------------|
| `cluster.xml` | Single-node cluster definition | No |
| `keeper.xml` | Embedded Keeper config (replaces ZooKeeper) | No |

### DNSmasq-TFTP (`/aios/configs/dnsmasq/`)
| File | Purpose | Credentials? |
|------|---------|-------------|
| `SEP00270DC01C92.cnf.xml` | Cisco 7962 phone SEP config (UDP→TCP fixed) | plaintext (9000pass) |
| `XMLDefault.cnf.xml` | Default phone config | No |
| `dialplan.xml` | Phone dial plan | No |
| `g3-tones.xml` | Tone definitions | No |
| `dnsmasq-tftp.conf` | TFTP-only server config (no DHCP) | No |
| `dnsmasq.conf` | Full DHCP+TFTP config (temp/ONT unplugged) | No |
| Firmware `.loads` files | SIP42.8-5-4S, SIP42.9-4-2SR3-1S | No |

### Asterisk (`/aios/configs/asterisk/`)
| File | Purpose | Credentials? |
|------|---------|-------------|
| `Dockerfile.asterisk` | Source compile, entrypoint | No |
| `docker-entrypoint.sh` | envsubst at runtime | No |
| `pjsip.conf` | SIP endpoints + trunk | `${VAR}` placeholders only |
| `ari.conf` | ARI API user | `${VAR}` placeholders only |
| `extensions.conf` | Dialplan | No |
| `asterisk.conf` | Directory paths | No |
| `http.conf` | HTTP/ARI server | No |
| `modules.conf` | Module autoload | No |
| `rtp.conf` | RTP port range | No |
| `logger.conf` | Logging config | No |
| `voicemail.conf` | Voicemail | No |
| `ai-agent.agi` | AI bridge script | No |
| `ai-agent.sh` | Shell helper | No |

### Vault (`/aios/configs/vault/`)
| File | Purpose | Status |
|------|---------|--------|
| `config.hcl` | Config file (unused) | Replaced by VAULT_LOCAL_CONFIG |

---

## 6. KEY PATHS

| Path | Purpose | Git? |
|------|---------|------|
| `/aios/` | Project root | ✅ |
| `/aios/docs/` | Architecture, SOPs, security, checkpoint | ✅ |
| `/aios/configs/` | Service configurations | ✅ |
| `/aios/configs/bifrost/` | LiteLLM gateway config | ✅ |
| `/aios/configs/clickhouse/` | ClickHouse cluster + keeper configs | ✅ |
| `/aios/scripts/` | Automation tools | ✅ |
| `/aios/ansible/` | Server setup playbooks | ✅ |
| `/aios/data/` | Runtime data (volumes, bind mounts) | ❌ (.gitignore) |
| `/aios/.env` | Environment secrets | ❌ (.gitignore) |
| `/aios/.vault-keys` | Vault unseal keys + root token | ❌ (.gitignore) |
| `/aios/n8n/` | Workflows (future) | ✅ |

---

## 7. SERVICE DEPENDENCIES

```
Vault ──┬── PostgreSQL (dynamic creds, future)
         ├── Asterisk (secrets, future)
         └── Bifrost (API keys, future)

PostgreSQL ──┬── Bifrost (virtual keys, model DB)
             ├── Langfuse (observability DB)
             ├── Keycloak (user store)
             └── n8n (workflow state, future)

Bifrost ──┬── Ollama (local inference — Mistral 7B, Qwen2.5 7B, Llama 3.2 3B)
          ├── OpenRouter (cloud fallback — Claude 4 Sonnet, Gemma 4, GPT-4o)
          └── Langfuse (LLM call logging, future)

Ollama ──── NVIDIA Quadro M4000 (8GB VRAM) — GPU inference via nvidia-container-toolkit

ClickHouse ── Langfuse (trace storage)

Asterisk ──┬── Bifrost (AI agent calls, future)
           ├── MQTT (events, future)
           └── Langfuse (logging, future)
```

---

## 8. OLLAMA MODELS

| Model in Ollama | Size | Quantization | Used By Bifrost As | Status |
|-----------------|------|-------------|-------------------|--------|
| mistral:latest | 7.2B | Q4_K_M (4.4 GB) | mistral-7b | ✅ verified |
| qwen2.5:latest | 7.6B | Q4_K_M | qwen-2.5-7b | 🟡 pulled, untested |
| llama3.2:latest | 3.2B | Q4_K_M | llama-3-8b | 🟡 pulled, untested (3.2B ≠ 8B — mismatched) |

---

*Created May 21, 2026 • Updated May 24, 2026 — AIOS Inventory*
