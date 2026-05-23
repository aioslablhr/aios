# AIOS — Complete Resource Inventory
## Single source of truth for every service, port, credential, and dependency

---

## 1. SERVICES

| Service | Container | Image | Zone | IP | Ports | Status | Compose Line |
|---------|-----------|-------|------|----|-------|--------|-------------|
| PostgreSQL | aios-postgres | postgres:16-alpine | data | 10.30.0.10 | 5432 | ✅ healthy | 36 |
| Qdrant | aios-qdrant | qdrant/qdrant:latest | data | 10.30.0.20 | 6333, 6334 | ✅ healthy | 58 |
| Redis | aios-redis | redis:7-alpine | data | 10.30.0.30 | 6379 | ✅ healthy | — |
| MinIO | aios-minio | minio/minio:latest | data | 10.30.0.40 | 9000, 9001 | ✅ healthy | — |
| Vault | aios-vault | hashicorp/vault:latest | app (host) | 10.0.0.100 | 8200 | ✅ unsealed | 85 |
| Keycloak | aios-keycloak | quay.io/keycloak/keycloak:26.1 | app | 10.20.0.40 | 8080 | ✅ healthy | — |
| Traefik | aios-traefik | traefik:v3.3 | dmz | 10.10.0.10 | 80, 443 | ✅ healthy | — |
| CrowdSec | aios-crowdsec | crowdsecurity/crowdsec:latest | dmz | 10.10.0.11 | 8080 | ✅ healthy | — |
| GitOps | aios-gitops | alpine:latest | app | 10.20.0.100 | — | ✅ healthy | 84 |
| Hermes | aios-hermes | alpine:latest | app | 10.20.0.70 | — | ✅ healthy | 120 |
| Dashy | aios-dashy | lissy93/dashy:latest | dmz | 10.60.0.70 | 80 | ✅ live | — |
| DNSmasq-TFTP | aios-dnsmasq-tftp | andyshinn/dnsmasq | host | 10.0.0.100 | 69/udp | ✅ healthy (external image) | — |
| Asterisk | aios-asterisk | aios-asterisk:latest (source) | host | 10.0.0.100 | 5060/udp, 5061/tcp, 8088, 10000-20000/udp | ✅ healthy | 142 |

### Services NOT in compose (orphan/manual)
Traefik, Dashy, Keycloak, CrowdSec, Redis, MinIO were deployed separately.
Need to be added to `docker-compose-aios.yml` or `docker-compose-apps.yml`.

---

## 2. DOCKER NETWORKS

| Network | Subnet | Internal | Used By |
|---------|--------|----------|---------|
| aios-dmz | 10.10.0.0/24 | no | Traefik, CrowdSec |
| aios-app | 10.20.0.0/24 | no | Vault (host net), Keycloak, GitOps, Hermes |
| aios-data | 10.30.0.0/24 | **yes** | PostgreSQL, Qdrant, Redis, MinIO |
| aios-ai | 10.40.0.0/24 | no | Bifrost, Ollama, vLLM (future) |
| aios-voice | 10.50.0.0/24 | no | Asterisk (host net), MQTT (future) |
| aios-mon | 10.60.0.0/24 | no | Langfuse, Grafana, Dashy (future) |
| aios-foss | 10.70.0.0/24 | no | ERPNext, Odoo, Twenty CRM (future) |

---

## 3. VOLUMES

| Volume | Mount | Service |
|--------|-------|---------|
| postgres-data | — | PostgreSQL |
| qdrant-data | — | Qdrant |
| minio-data | — | MinIO |
| crowdsec-data | — | CrowdSec |
| vault-data (unused) | — | Vault (switched to bind mount) |
| asterisk-data | — | Asterisk |
| asterisk-log | — | Asterisk |
| mosquitto-data | — | MQTT (future) |
| mosquitto-log | — | MQTT (future) |
| Bind: /aios/data/vault | /vault/file | Vault (raft storage) |

---

## 4. CREDENTIALS

| Credential | Location | Type | Notes |
|------------|----------|------|-------|
| Server sudo | `.env` → `SERVER_PASS` | plaintext | chmod 600 |
| Cloudflare API | `.env` → `CLOUDFLARE_API_KEY` | plaintext | DNS:Edit scope |
| CrowdSec API | `.env` → `CROWDSEC_API_KEY` | plaintext | — |
| Ext 100 (Admin) | `.env` → `EXT_100_SECRET` | plaintext | Injected via envsubst |
| Ext 101 (Support) | `.env` → `EXT_101_SECRET` | plaintext | Injected via envsubst |
| Ext 102 (AI Agent) | `.env` → `EXT_102_SECRET` | plaintext | Injected via envsubst |
| Ext 103 (Test) | `.env` → `EXT_103_SECRET` | plaintext | Injected via envsubst |
| Ext 104 (Android) | `.env` → `EXT_104_SECRET` | plaintext | Injected via envsubst |
| Ext 9000 (Cisco) | `.env` → `EXT_9000_SECRET` | plaintext | Injected via envsubst |
| ARI admin | `.env` → `ARI_ADMIN_PASSWORD` | plaintext | Injected via envsubst |
| Vault root token | `.vault-keys` | plaintext | chmod 600, NOT in git |
| Vault unseal keys | `.vault-keys` | plaintext | chmod 600, NOT in git |
| Anthropic API | `.env` → `<from Vault>` | missing | Vault ready, migrate needed |
| OpenAI API | `.env` → `<from Vault>` | missing | Vault ready, migrate needed |
| OpenRouter API | `.env` → `<from Vault>` | missing | Vault ready, migrate needed |

---

## 5. CONFIG FILES

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
| `/aios/docs/` | Architecture, SOPs, security | ✅ |
| `/aios/configs/` | Service configurations | ✅ |
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

PostgreSQL ──┬── Supabase (future)
             ├── Keycloak (user store)
             └── n8n (workflow state, future)

Asterisk ──┬── Bifrost (AI agent calls, future)
           ├── MQTT (events, future)
           └── Langfuse (logging, future)
```

---

*Created May 21, 2026 — AIOS Inventory*
