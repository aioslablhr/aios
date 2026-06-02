# AIOS — All Credentials Reference
## URL, User, Password for every service

---

## Web Dashboards (public HTTPS endpoints)

| Service | URL | Username | Password | Notes |
|---------|-----|----------|----------|-------|
| Dashy (Home) | https://socialbeesai.com | — | — | Landing page, 33 tiles |
| Traefik Dashboard | https://admin.socialbeesai.com | — | — | Reverse proxy status |
| n8n | https://n8n.socialbeesai.com | (first user to sign up) | — | Workflow automation |
| Bifrost / LiteLLM | https://ai.socialbeesai.com | API key: sk-aios-master-admin-key-change-me | — | AI Gateway — Swagger UI |
| Langfuse | https://langfuse.socialbeesai.com | (create account on first visit) | — | LLM Observability |
| Keycloak | https://keycloak.socialbeesai.com | admin | admin | SSO / Identity |
| Vault | https://vault.socialbeesai.com | Root token in .vault-keys on server | — | Secrets management |
| Dograh UI | https://voice.socialbeesai.com | Sign up on first visit (first user = admin) | — | Voice agent orchestration |
| MinIO Console | https://data.socialbeesai.com/minio | admin | minioadmin | S3 storage |
| Grafana | https://monitor.socialbeesai.com/grafana | admin | grafana_admin_2026 | Metrics dashboards |
| Prometheus | https://monitor.socialbeesai.com/prometheus | — | — | Metrics backend |
| Portainer | https://monitor.socialbeesai.com/portainer | (create on first visit) | — | Docker management |
| cAdvisor | https://monitor.socialbeesai.com/cadvisor | — | — | Container monitoring |
| Qdrant Dashboard | https://qdrant.socialbeesai.com/dashboard | API key: aios_qdrant_2026 | — | Vector database UI |
| ClickHouse Play | https://clickhouse.socialbeesai.com | default | clickhouse | Analytics queries |
| Frigate NVR | https://frigate.socialbeesai.com | — | — | AI surveillance |
| Flowise | https://app.socialbeesai.com/flowise | admin | admin | Visual LLM builder |
| MCP Server | https://mcp.socialbeesai.com | — | — | Model Context Protocol |

---

## Internal Services (Docker IPs — no web UI)

| Service | IP:Port | Credentials | Notes |
|---------|---------|-------------|-------|
| PostgreSQL | 10.30.0.10:5432 | aios / aios_secret_2026 | Main DB. DBs: aios, dograh, langfuse, litellm, keycloak |
| N8N DB | 10.20.0.15:5432 | n8n / 21e8c7e99182e353a7326dff9b40d4ec | n8n dedicated PostgreSQL |
| Redis | 10.30.0.30:6379 | — | Cache + queue |
| Qdrant API | 10.30.0.20:6333 | API key: aios_qdrant_2026 | Vector search |
| MinIO API | 10.30.0.40:9000 | admin / minioadmin | S3 API endpoint |
| Ollama API | 10.40.0.20:11434 | — | Local LLM (embeddings, vision) |
| Bifrost API | 10.40.0.10:4000 | Key: sk-aios-master-admin-key-change-me | OpenAI-compatible endpoint |
| Dograh API | 10.50.0.30:8000 | JWT secret for backend: aios-dograh-jwt-secret-2026 | Voice backend |
| Dograh UI | 10.50.0.31:3010 | Sign up on first visit | Voice dashboard |
| Chatterbox TTS | 10.40.0.30:4123 | — | GPU text-to-speech (primary, Dograh auto-selects) |
| Kokoro TTS | 10.40.0.31:8880 | — | CPU text-to-speech (fallback, Dograh auto-selects) |
| Mosquitto MQTT | 10.50.0.20:1883 | — | Event bus |
| Asterisk ARI | 10.0.0.100:8088 | ai / 95vt3r6ke1w8lgqg6qpcui8e | PBX API |
| ClickHouse | 10.60.0.11:8123 | default / clickhouse | Analytics DB |
| Grafana Loki | 10.60.0.40:3100 | — | Log aggregation |
| Prometheus | 10.60.0.20:9090 | — | Metrics API |
| GitOps Agent | 10.20.0.100 | — | Auto-deploy (no UI) |
| Hermes Agent | 10.20.0.70 | — | 24/7 ops (no UI) |

---

## Asterisk SIP Extensions

| Extension | Password | Device |
|-----------|----------|--------|
| 100 | 100pass | Softphone |
| 101 | pz27i3w0danj0mpc | Softphone |
| 102 | lry4ufds5py826y4 | Softphone |
| 103 | 103pass | Softphone |
| 104 | 104pass | Softphone |
| 9000 | 9000pass | Cisco 7962G (IP: 10.0.0.12) |
| Voicemail | 1234 | (all extensions) |

---

## API Keys & Cloud

| Service | Key | Notes |
|---------|-----|-------|
| OpenRouter | sk-or-v1-0855e04fc... | **REAL KEY** — free tier, 25+ $0 models |
| Cloudflare | (see .env on server) | DNS:Edit scope, admin@socialbeesai.com |
| CrowdSec | (see .env on server) | WAF bouncer key |
| MinIO | admin / minioadmin | Console + API |

---

## Vault (secrets management)
- **URL**: https://vault.socialbeesai.com
- **Root token**: see `/aios/.vault-keys` on server (NOT in git)
- **Unseal keys**: 5 keys in `/aios/.vault-keys` on server
- Status: **Running, unsealed** — migration target for .env secrets

---

## SSH Access
- **Host**: 10.0.0.100
- **User**: ai
- **Password**: Lahore*999
- **OS**: Ubuntu 22.04.5 LTS

---

*Updated May 26, 2026 — AIOS Credentials Reference*
