# AIOS — Session Checkpoint v4.4

## This Session (May 26) — Architecture Tune & Refine

### OpenRouter Key & Bifrost Upgrade
- **Real OpenRouter API key** set: `sk-or-v1-0855e04fc...` (was placeholder)
- **Bifrost model list** expanded from 6 to 28 models (25 OpenRouter $0 + 3 local Ollama)
- **Bifrost config** fixed: removed `database_url` (LiteLLM DB was storing stale models, caused 400 errors)
- **Bifrost config** simplified: hardcoded API key in config (no DB dependency), env vars for local models
- **Bifrost tested**: `openrouter-free`, `gemma-4-31b`, `deepseek-v4`, `auto-router` all working
- Dograh images switched from Docker Hub `dograhai/*` (paid/cloud requiring Stack Auth) to `ghcr.io/dograh-hq/*` (OSS)

### Architecture Audit (May 26)
- All 35 containers running and verified
- Public endpoints: 403 via CrowdSec (expected — Dev PC IP not whitelisted)
- Internal endpoints: 13/15 core services responding 200
- Known stale issues documented below

## Current State: Phase 4 — All Services Deployed & Verified (May 26, 2026)

### 35 Containers Running

#### DMZ Zone — 10.10.0.0/24
| Service | Container | IP | Port | Status |
|---------|-----------|----|------|--------|
| Traefik | aios-traefik | 10.10.0.10 | 80, 443 | running — reverse proxy, SSL termination |
| CrowdSec | aios-crowdsec | 10.10.0.11 | 8080 | running — WAF bouncer active |

#### App Zone — 10.20.0.0/24
| Service | Container | IP | Port | Status |
|---------|-----------|----|------|--------|
| Keycloak | aios-keycloak | 10.20.0.40 | 8080 | running (health starting) — SSO, admin console accessible |
| n8n | aios-n8n | 10.20.0.10 | 5678 | running — workflow orchestration, queue mode |
| n8n-db | aios-n8n-db | 10.20.0.15 | 5432 | healthy — n8n dedicated PostgreSQL |
| n8n-worker-1 | aios-n8n-worker-1 | 10.20.0.13 | — | running — concurrency=10 |
| n8n-worker-2 | aios-n8n-worker-2 | 10.20.0.12 | — | running — concurrency=10 |
| Flowise | aios-flowise | 10.20.0.20 | 3000 | running — visual LLM builder (app.socialbeesai.com/flowise) |
| MCP Server | aios-mcp | 10.20.0.30 | 8000 | running — Model Context Protocol (mcp.socialbeesai.com) |
| GitOps | aios-gitops | 10.20.0.100 | — | running — polls GitHub every 30s |
| Hermes | aios-hermes | 10.20.0.70 | — | running — 24/7 autonomous ops |

#### Data Zone — 10.30.0.0/24 (internal:true — NO internet access)
| Service | Container | IP | Port | Status |
|---------|-----------|----|------|--------|
| PostgreSQL | aios-postgres | 10.30.0.10 | 5432 | healthy — pgvector 0.8.0, DBs: aios, dograh, langfuse, litellm, keycloak |
| Qdrant | aios-qdrant | 10.30.0.20 | 6333, 6334 | healthy — vector DB, RAG fallback |
| Redis | aios-redis | 10.30.0.30 | 6379 | healthy — n8n queue + cache |
| MinIO | aios-minio | 10.30.0.40 | 9000, 9001 | **unhealthy** — need check |

#### AI Zone — 10.40.0.0/24
| Service | Container | IP | Port | Status |
|---------|-----------|----|------|--------|
| Bifrost (LiteLLM) | aios-bifrost | 10.40.0.10 | 4000 | healthy — AI Gateway, 28 models |
| Ollama | aios-ollama | 10.40.0.20 | 11434 | healthy — nomic-embed-text + LLaVA |
| Chatterbox TTS | aios-chatterbox | 10.40.0.30 | 4123 | running (starting) — GPU text-to-speech |
| Frigate NVR | aios-frigate | 10.40.0.50 | 5000 | healthy — AI object detection |

#### Voice Zone — 10.50.0.0/24
| Service | Container | IP | Port | Status |
|---------|-----------|----|------|--------|
| Mosquitto MQTT | aios-mosquitto | 10.50.0.20 | 1883, 9001 | running — event bus |
| Dograh API | aios-dograh-api | 10.50.0.30 | 8000 | healthy — voice agent orchestration (OSS GHCR) |
| Dograh UI | aios-dograh-ui | 10.50.0.31 | 3010 | running — voice agent dashboard (OSS GHCR) |

#### Monitoring Zone — 10.60.0.0/24
| Service | Container | IP | Port | Status |
|---------|-----------|----|------|--------|
| Langfuse | aios-langfuse | 10.60.0.10 | 3000 | running — LLM observability |
| ClickHouse | aios-clickhouse | 10.60.0.11 | 8123, 9000 | healthy — Langfuse trace storage |
| Prometheus | aios-prometheus | 10.60.0.20 | 9090 | running — metrics backend |
| Grafana | aios-grafana | 10.60.0.30 | 3000 | running — dashboards |
| Loki | aios-loki | 10.60.0.40 | 3100 | running — log aggregation |
| Portainer | aios-portainer | 10.60.0.50 | 9000 | running — Docker management UI |
| cAdvisor | aios-cadvisor | 10.60.0.60 | 8080 | healthy — container resource monitoring |
| Node Exporter | aios-node-exporter | 10.60.0.61 | 9100 | running — host metrics exporter |
| Dashy | aios-dashy | 10.60.0.70 | 8080 | running (starting) — service dashboard |

#### Host Network Mode (10.0.0.100)
| Service | Container | IP | Port | Status |
|---------|-----------|----|------|--------|
| Vault | aios-vault | 10.0.0.100 | 8200 | unsealed — secrets management |
| Asterisk | aios-asterisk | 10.0.0.100 | 5060/udp, 5061/tcp, 10000-20000/udp | healthy — SIP PBX |
| DNSmasq-TFTP | aios-dnsmasq-tftp | 10.0.0.100 | 69/udp | running — Cisco phone provisioning |

---

### 14 Public Endpoints — All via Traefik HTTPS

| URL | Target | Status |
|-----|--------|--------|
| https://socialbeesai.com | Dashy | 403 (CrowdSec) — was 200 before CrowdSec |
| https://admin.socialbeesai.com | Traefik Dashboard | 403 (CrowdSec) |
| https://n8n.socialbeesai.com | n8n | 403 (CrowdSec) |
| https://ai.socialbeesai.com | Bifrost | 403 (CrowdSec) |
| https://langfuse.socialbeesai.com | Langfuse | 403 (CrowdSec) |
| https://keycloak.socialbeesai.com | Keycloak | 403 (CrowdSec) |
| https://vault.socialbeesai.com | Vault | 403 (CrowdSec) |
| https://voice.socialbeesai.com | Dograh UI | 403 (CrowdSec) |
| https://app.socialbeesai.com/flowise | Flowise | 403 (CrowdSec) |
| https://data.socialbeesai.com/minio | MinIO Console | 403 (CrowdSec) |
| https://monitor.socialbeesai.com/grafana | Grafana | 403 (CrowdSec) |
| https://frigate.socialbeesai.com | Frigate NVR | 403 (CrowdSec) |
| https://clickhouse.socialbeesai.com | ClickHouse | 403 (CrowdSec) |
| https://mcp.socialbeesai.com | MCP Server | 403 (CrowdSec) |

**Note**: All public endpoints return 403 via external IP due to CrowdSec WAF. Internal Docker DNS resolves correctly (200s verified from server).

---

### Bifrost — 28 Available Models

| Category | Models |
|----------|--------|
| **Local Ollama (free)** | mistral-7b, qwen-2.5-7b, llama-3-8b |
| **OpenRouter $0 tier** | openrouter-free, gemma-4-31b, gemma-4-26b, llama-70b, llama-3b, deepseek-v4, qwen-coder, qwen-80b, hermes-405b, cobuddy, owl-alpha, liquid-thinking, liquid-instruct, minimax-m2, gpt-oss-120b, gpt-oss-20b, nemotron-reasoning, nemotron-nano-30b, nemotron-120b, nemotron-vl, nemotron-9b, glm-4, dolphin-24b, poolside-xs, poolside-m |

Routing: Local first → OpenRouter fallback. Tested working: cobuddy, openrouter-free, gemma-4-31b, deepseek-v4, auto-router.

---

### Known Issues

1. **MinIO unhealthy** — container shows `(unhealthy)`, health check failing
2. **Keycloak health check** staying `(health: starting)` — service works (admin console accessible)
3. **CrowdSec returning 403** on all public endpoints from external IP — need to whitelist Dev PC or disable for testing
4. **Prometheus targets**: bifrost/n8n/frigate metrics endpoints `down` — need `/metrics` endpoint enabled upstream
5. **WireGuard VPN** not deployed — no compose service
6. **Open WebUI** not deployed — route exists at `chat.socialbeesai.com` (502)
7. **Supabase** not deployed — only Postgres running (no Supabase Studio)
8. **IP Cameras** — RTSP feeds not configured for Frigate
9. **No Langfuse admin user** created yet — observability pipeline incomplete
10. **Vault** on host networking (not Docker network) — needs migration to `aios-app` zone
11. **MCP SSE** returns 421 through Traefik — SSE-specific proxy config required
12. **Portainer** requires admin account creation in browser session (first visit)
13. **Chatterbox** health still starting — needs investigation

---

### Next Steps

1. Fix MinIO health check — investigate minio container logs
2. Fix CrowdSec 403 on public endpoints — whitelist Dev PC IP
3. Deploy WireGuard VPN (add compose service + route)
4. Deploy Open WebUI (add compose service + image + route `chat.socialbeesai.com`)
5. Configure Frigate — add camera RTSP feeds, enable metrics endpoint
6. Fix Keycloak health check — update health probe for v26.1
7. Set up Langfuse admin user for LLM observability pipeline
8. Fix MCP SSE 421 through Traefik
9. Build 4 use case workflows (Surveillance, HR, CRM, Voice Receptionist)
10. Migrate Vault to `aios-app` zone

---

### Credentials Quick Ref

| Service | URL | User | Pass |
|---------|-----|------|------|
| Dashy | https://socialbeesai.com | — | — |
| n8n | https://n8n.socialbeesai.com | (browser session) | — |
| Bifrost | https://ai.socialbeesai.com | sk-aios-master-admin-key-change-me | — |
| Langfuse | https://langfuse.socialbeesai.com | (create account) | — |
| Keycloak | https://keycloak.socialbeesai.com | admin | admin |
| Vault | https://vault.socialbeesai.com | root token in .vault-keys | — |
| MinIO | https://data.socialbeesai.com/minio | admin | minioadmin |
| Grafana | https://monitor.socialbeesai.com/grafana | admin | grafana_admin_2026 |
| Dograh | https://voice.socialbeesai.com | Sign up on first visit | — |
| Frigate | https://frigate.socialbeesai.com | — | — |
| Flowise | https://app.socialbeesai.com/flowise | admin | admin |
| Portainer | https://monitor.socialbeesai.com/portainer | (create on first visit) | — |
| Qdrant | https://qdrant.socialbeesai.com/dashboard | API key: aios_qdrant_2026 | — |
| ClickHouse | https://clickhouse.socialbeesai.com | default | clickhouse |
| Full creds: `docs/ref/credentials.md` | | | |

*Updated May 26, 2026 — AIOS Session Checkpoint v4.4*
