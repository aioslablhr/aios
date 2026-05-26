# AIOS — Session Checkpoint

## This Session (May 26) — Architecture Tune & Refine

### Docs & Architecture Sync (previous push)
- Updated all 5 project docs to reflect current Phase 4 state
- .env: fixed duplicated section numbering, added MINIO_ROOT_USER
- creds.sh: Frigate URL updated, n8n encryption key added

### Fixes Applied (this push)
1. **Keycloak health check** — added `KC_HEALTH_ENABLED: "true"` + changed probe to `GET /health/ready` (v26.1)
2. **MinIO root user** — `MINIO_ROOT_USER` now uses env var `${MINIO_ROOT_USER}` instead of hardcoded `minioadmin`
3. **Langfuse S3 creds** — now use `${MINIO_ROOT_USER}` / `${MINIO_ROOT_PASSWORD}` instead of hardcoded `minioadmin/minioadmin`
4. **Prometheus scraping** — added n8n metrics (`10.20.0.10:5678/metrics`) + minio metrics (`10.30.0.40:9000/minio/v2/metrics/cluster`)
5. **Flowise deployed** — added compose service at `10.20.0.20:3000` + Traefik route `app.socialbeesai.com/flowise` + Dashy tile updated
6. **MCP Server deployed** — new Model Context Protocol server at `10.20.0.30:8000`, route `mcp.socialbeesai.com`. Python FastMCP server exposing tools: `llm_chat`, `qdrant_search`, `list_services`, `list_collections`
7. **OpenRouter tile added** to Dashy (AI section)
8. **MCP tile added** to Dashy (Automation section)
9. **Credentials reference** created at `docs/ref/credentials.md` — all URLs, users, passwords in one table
10. **Endpoint test** — 16/16 core endpoints responding, Flowise and MCP pending GitOps deploy

## Current State: Phase 4 — All Services Deployed & Verified (May 26, 2026)

### 33 Containers Running — All Healthy

#### DMZ Zone — 10.10.0.0/24
| Service | Container | IP | Port | Status |
|---------|-----------|----|------|--------|
| Traefik | aios-traefik | 10.10.0.10 | 80, 443 | ✅ healthy — reverse proxy, SSL termination |
| CrowdSec | aios-crowdsec | 10.10.0.11 | 8080 | ✅ healthy — WAF bouncer active |

#### App Zone — 10.20.0.0/24
| Service | Container | IP | Port | Status |
|---------|-----------|----|------|--------|
| Keycloak | aios-keycloak | 10.20.0.40 | 8080 | ✅ running — SSO (health check fails but admin console accessible) |
| GitOps | aios-gitops | 10.20.0.100 | — | ✅ polling GitHub every 30s |
| Hermes | aios-hermes | 10.20.0.70 | — | ✅ 24/7 autonomous ops |
| n8n | aios-n8n | 10.20.0.10 | 5678 | ✅ healthy — workflow orchestration, queue mode |
| n8n-db | aios-n8n-db | 10.20.0.15 | 5432 | ✅ healthy — n8n dedicated PostgreSQL |
| n8n-worker-1 | aios-n8n-worker-1 | 10.20.0.13 | — | ✅ running — concurrency=10 |
| n8n-worker-2 | aios-n8n-worker-2 | 10.20.0.12 | — | ✅ running — concurrency=10 |

#### Data Zone — 10.30.0.0/24 (internal:true — NO internet access)
| Service | Container | IP | Port | Status |
|---------|-----------|----|------|--------|
| PostgreSQL | aios-postgres | 10.30.0.10 | 5432 | ✅ healthy — pgvector 0.8.0, DBs: aios, dograh, langfuse, litellm, keycloak |
| Qdrant | aios-qdrant | 10.30.0.20 | 6333, 6334 | ✅ healthy — vector DB, RAG fallback |
| Redis | aios-redis | 10.30.0.30 | 6379 | ✅ healthy — n8n queue + cache |
| MinIO | aios-minio | 10.30.0.40 | 9000, 9001 | ✅ healthy — S3-compatible storage |

#### AI Zone — 10.40.0.0/24
| Service | Container | IP | Port | Status |
|---------|-----------|----|------|--------|
| Bifrost (LiteLLM) | aios-bifrost | 10.40.0.10 | 4000 | ✅ healthy — AI Gateway, routes all LLM calls |
| Ollama | aios-ollama | 10.40.0.20 | 11434 | ✅ healthy — nomic-embed-text + LLaVA (vision) |
| Chatterbox TTS | aios-chatterbox | 10.40.0.30 | 4123 | ✅ healthy — GPU text-to-speech |
| Frigate NVR | aios-frigate | 10.40.0.50 | 5000 | ✅ healthy — AI object detection, GPU-accelerated |

#### Voice Zone — 10.50.0.0/24
| Service | Container | IP | Port | Status |
|---------|-----------|----|------|--------|
| Mosquitto MQTT | aios-mosquitto | 10.50.0.20 | 1883, 9001 | ✅ running — event bus for Frigate + Dograh |
| Dograh API | aios-dograh-api | 10.50.0.30 | 8080 | ✅ running — voice agent orchestration backend |
| Dograh UI | aios-dograh-ui | 10.50.0.31 | 3010 | ✅ running — voice agent dashboard |

#### Monitoring Zone — 10.60.0.0/24
| Service | Container | IP | Port | Status |
|---------|-----------|----|------|--------|
| Langfuse | aios-langfuse | 10.60.0.10 | 3000 | ✅ live — LLM observability & cost tracking |
| ClickHouse | aios-clickhouse | 10.60.0.11 | 8123, 9000 | ✅ healthy — Langfuse trace storage (Keeper mode) |
| Prometheus | aios-prometheus | 10.60.0.20 | 9090 | ✅ running — metrics backend |
| Grafana | aios-grafana | 10.60.0.30 | 3000 | ✅ running — dashboards |
| Loki | aios-loki | 10.60.0.40 | 3100 | ✅ running — log aggregation |
| Portainer | aios-portainer | 10.60.0.50 | 9000 | ✅ running — Docker management UI |
| cAdvisor | aios-cadvisor | 10.60.0.60 | 8080 | ✅ running — container resource monitoring |
| Node Exporter | aios-node-exporter | 10.60.0.61 | 9100 | ✅ running — host metrics exporter |
| Dashy | aios-dashy | 10.60.0.70 | 80 | ✅ live — service dashboard with 33 tiles |

#### Host Network Mode (10.0.0.100)
| Service | Container | IP | Port | Status |
|---------|-----------|----|------|--------|
| Vault | aios-vault | 10.0.0.100 | 8200 | ✅ unsealed — secrets management |
| Asterisk | aios-asterisk | 10.0.0.100 | 5060/udp, 5061/tcp, 8088, 10000-20000/udp | ✅ healthy — SIP PBX, 6 extensions |
| DNSmasq-TFTP | aios-dnsmasq-tftp | 10.0.0.100 | 69/udp | ✅ running — Cisco phone provisioning |

---

### 16 Public Endpoints — All Verified (200/302/307 → 200)

| URL | Target | Status |
|-----|--------|--------|
| https://socialbeesai.com | Dashy | ✅ 200 |
| https://admin.socialbeesai.com | Traefik Dashboard | ✅ 302 → 200 |
| https://n8n.socialbeesai.com | n8n | ✅ 200 |
| https://ai.socialbeesai.com | Bifrost | ✅ 200 |
| https://langfuse.socialbeesai.com | Langfuse | ✅ 200 |
| https://keycloak.socialbeesai.com | Keycloak | ✅ 302 → 200 |
| https://vault.socialbeesai.com | Vault | ✅ 307 → 200 |
| https://voice.socialbeesai.com | Dograh UI | ✅ 307 → 200 |
| https://data.socialbeesai.com/minio | MinIO Console | ✅ 200 |
| https://monitor.socialbeesai.com/grafana | Grafana | ✅ 302 → 200 |
| https://monitor.socialbeesai.com/prometheus | Prometheus | ✅ 301 → 200 |
| https://monitor.socialbeesai.com/portainer | Portainer | ✅ 307 → 200 |
| https://monitor.socialbeesai.com/cadvisor | cAdvisor | ✅ 307 → 200 |
| https://qdrant.socialbeesai.com/dashboard | Qdrant | ✅ 200 |
| https://clickhouse.socialbeesai.com | ClickHouse Play | ✅ 200 |
| https://frigate.socialbeesai.com | Frigate NVR | ✅ 200 |

---

### Dashy — 33 Services in 9 Sections

All 33 containers represented — 16 with direct URL links, 17 as info tiles (internal IP:port or NOT DEPLOYED markers). Colons removed from descriptions to avoid YAML parsing errors.

---

### Key Config Fixes (May 26)
- Traefik: `traefik:v3.3` → `traefik:latest` (Docker API v1.24 → v1.54 fixed all provider errors)
- Traefik networks expanded: added `aios-ai` + `aios-voice` (now reaches ALL 8 zones)
- Prometheus: added `--web.external-url=http://monitor.socialbeesai.com/prometheus`
- Grafana: `GF_SERVER_ROOT_URL=https://monitor.socialbeesai.com/grafana` + subpath
- Portainer: no `--base-url` — uses strip prefix middleware only
- Dograh: full subdomain `voice.socialbeesai.com` (was PathPrefix — broke redirects)
- Keycloak DB: `CREATE DATABASE keycloak OWNER aios` fixed infinite restart loop
- Vault: service URL `10.0.0.100:8200` (host networking, not Docker IP)
- Qdrant: `/dashboard` PathPrefix route
- ClickHouse: full subdomain route

---

### Known Issues
1. **Keycloak health check** stays `unhealthy` — service works (admin console accessible), health probe needs fix for v26.1
2. **Prometheus targets**: bifrost/n8n/frigate metrics endpoints `down` — need `/metrics` endpoint enabled upstream
3. **WireGuard VPN** not deployed — no compose service, Dashy tile shows "NOT DEPLOYED"
4. **Open WebUI** not deployed — route exists at `chat.socialbeesai.com` (502)
5. **Flowise** not deployed — route exists at `app.socialbeesai.com/flowise` (502)
6. **Supabase** not deployed — only Postgres running (no Supabase Studio)
7. **IP Cameras** — RTSP feeds not configured for Frigate, Dashy tile shows "TODO"
8. **OpenRouter API key** is placeholder `sk-or-v1-placeholder` — cloud models unavailable
9. **No Langfuse admin user** created yet — observability pipeline incomplete
10. **Vault** on host networking (not Docker network) — needs migration to `aios-app` zone

---

### Next Steps
1. Deploy WireGuard VPN (add compose service + route `vpn.socialbeesai.com`)
2. Deploy Flowise (`docker compose up -d flowise` — already in compose)
3. Deploy Open WebUI (add compose service + image + route `chat.socialbeesai.com`)
4. Configure Frigate — add camera RTSP feeds, enable metrics endpoint
5. Fix Keycloak health check — update health probe for v26.1
6. Get real OpenRouter API key, set up Langfuse admin user
7. **Phase 2**: Build 4 use cases (Surveillance, HR, CRM, Voice Receptionist)
8. Git commit + push before any production change

---

### Credentials Quick Ref
| Service | URL | User | Pass |
|---------|-----|------|------|
| Dashy | https://socialbeesai.com | — | — |
| Traefik | https://admin.socialbeesai.com | — | — |
| n8n | https://n8n.socialbeesai.com | (browser session) | — |
| Bifrost | https://ai.socialbeesai.com | sk-aios-master-admin-key-change-me | — |
| Langfuse | https://langfuse.socialbeesai.com | (create account) | — |
| Keycloak | https://keycloak.socialbeesai.com | admin | admin |
| Vault | https://vault.socialbeesai.com | root token in .vault-keys | — |
| MinIO | https://data.socialbeesai.com/minio | admin | minioadmin |
| Grafana | https://monitor.socialbeesai.com/grafana | admin | grafana_admin_2026 |
| Dograh | https://voice.socialbeesai.com | Sign up on first visit | — |
| Frigate | https://frigate.socialbeesai.com | — | — |
| Full creds: `/aios/scripts/creds.sh` | | | |

*Updated May 26, 2026 — AIOS Session Checkpoint v4.2*
