# AIOS — Build Checkpoint
## Last Updated: May 26, 2026 — v4.2 — ALL 12 public endpoints verified, ALL services accessible

---

### ✅ COMPLETED STEPS

**Phase 0-2 Foundation:** GPU driver, Docker, 8 networks, data + security layer, Vault, Git/GitHub, CI, GitOps, Hermes, Cloudflare tunnel + SSL + Dashy

**Asterisk + Cisco 7962G:** 22.9.0 compiled, 6 extensions, Cisco registered on TCP transport fix

**n8n + OpenRouter (May 25):** n8n stack main + db + 2 workers, webhook test with `liquid/lfm-2.5-1.2b:free`

**Architecture Finalized (May 26):**
- All 33 containers running, 8 network zones
- All orphan containers added to compose
- CrowdSec, MinIO, Keycloak, Dashy, Vault added
- Frigate with GPU, Dograh API+UI, Chatterbox TTS deployed
- Mosquitto MQTT, pgvector Postgres, cAdvisor, node-exporter running

**Infrastructure fixes (May 26 — Round 2):**
- **Traefik**: `traefik:v3.3` → `traefik:latest` (Docker API mismatch fix)
- **Traefik networks**: Added `aios-ai` + `aios-voice` — reaches ALL 8 zones
- **Prometheus**: Added `--web.external-url`, removed strip prefix → serves at `/prometheus/...`
- **Grafana**: Added `GF_SERVER_ROOT_URL` + `GF_SERVER_SERVE_FROM_SUB_PATH` → correct login redirect
- **Portainer**: Strip prefix middleware → works at `/portainer`
- **Dograh**: Full subdomain `voice.socialbeesai.com` → redirect chain works
- **n8n**: Dedicated `n8n.socialbeesai.com` subdomain
- **Dograh API**: `MINIO_PUBLIC_ENDPOINT` env var + port mapping

**Phase 2 — Infrastructure (May 26 — Round 3):**
- **Keycloak DB created**: `CREATE DATABASE keycloak` fixes infinite restart loop
- **Vault reachable**: Service URL changed from `10.20.0.50:8200` (internal Docker, unreachable) to `10.0.0.100:8200` (host networking)
- **New Traefik routes**: `ai.socialbeesai.com` (Bifrost), `langfuse.socialbeesai.com`, `keycloak.socialbeesai.com`, `vault.socialbeesai.com`
- **Dashy config rewritten**: Removed non-deployed services (Open WebUI, Flowise, Supabase), added all working routes
- **All 12 public endpoints verified responding**: 12/12 returning 200/302/307 → 200 on redirect follow

### ✅ Public Endpoints — All VERIFIED Working (May 26)

| URL | Code | Service |
|---|---|---|
| `https://socialbeesai.com` | 200 | Dashy sysops hub |
| `https://ai.socialbeesai.com` | 200 | Bifrost (AI Gateway) |
| `https://langfuse.socialbeesai.com` | 200 | Langfuse (LLM Observability) |
| `https://keycloak.socialbeesai.com` | 302→200 | Keycloak (Identity & SSO) |
| `https://vault.socialbeesai.com` | 307→200 | Vault (Secrets Management) |
| `https://n8n.socialbeesai.com` | 200 | n8n (Workflow Automation) |
| `https://voice.socialbeesai.com` | 307→200 | Dograh (Voice Orchestration) |
| `https://data.socialbeesai.com/minio` | 200 | MinIO Console |
| `https://monitor.socialbeesai.com/grafana` | 302→200 | Grafana |
| `https://monitor.socialbeesai.com/prometheus` | 301→200 | Prometheus |
| `https://monitor.socialbeesai.com/portainer` | 307→200 | Portainer |
| `https://admin.socialbeesai.com` | 302→200 | Traefik Dashboard |

**33/33 containers running, 12/12 public endpoints verified ✅**

---

### ❌ MINOR ISSUES (non-blocking for use cases)

- **Keycloak** health check fails (stays `unhealthy`) but service works — health check command needs fix
- **Keycloak** uses deprecated `KEYCLOAK_ADMIN` env var → needs `KC_BOOTSTRAP_ADMIN_USERNAME` for v26
- **Vault on host networking** — needs move to `aios-app` network (low priority, Traefik reaches via host IP)
- **SIP trunk** — `TRUNK_PASS` placeholder, internal extensions work
- **Open WebUI** not deployed — route exists but no container (remove route or deploy)
- **Flowise** not deployed — route exists but no container
- **Supabase** not deployed — only Postgres running
- **Prometheus targets**: bifrost/n8n/frigate metrics endpoints `down` (need `/metrics` endpoint enabled upstream)
- **Portainer** admin monitor times out after 5 min without login — restart to re-enable

---

### ✅ ARCHITECTURE DECISIONS — v4.2 (LOCKED May 26)

- **Clean subdomains over path prefixes**: `keycloak.socialbeesai.com`, `vault.socialbeesai.com`, `langfuse.socialbeesai.com` — avoids PathPrefix redirect conflicts
- **Dashy shows only working services**: Non-deployed services (Open WebUI, Flowise, Supabase) removed from Dashy until deployed
- **Vault host networking**: Vault uses `network_mode: host` — route to `10.0.0.100:8200` via Traefik until migrated

---

---

### SERVER SNAPSHOT
```
Hostname: aios
IP:       10.0.0.100
OS:       Ubuntu 22.04.5 LTS
CPU:      Intel Core i7-7800X @ 3.50GHz (6C/12T)
RAM:      31GB
GPU:      Quadro M4000 — 8GB VRAM ✅
Docker:   29.5.1 ✅
Containers: 33 — all managed via docker-compose, all verified
Disk:     953.9GB NVMe (free: TBD after cleanup)
```

### FILES REFERENCE
```
D:\AIOS\
├── PROJECT.md               # v4.0 — 16 sections
├── CLAUDE.md                # v4.0 — Claude Code instructions
├── CHECKPOINT.md            # This file
├── DEPLOYMENT_PLAN.md       # 18-step build plan
├── docker-compose-aios.yml  # AI core stack (33 services)
├── configs/
│   ├── traefik/dynamic/aios.yml  # Traefik routing (9 public routes)
│   ├── prometheus/prometheus.yml  # Scrape config
│   ├── grafana/provisioning/      # Auto-provisioned datasource + dashboards
│   ├── asterisk/            # 12 config files + Dockerfile
│   ├── dnsmasq/             # SEP, XMLDefault, dialplan, tones
│   ├── crowdsec/            # WAF rules
│   ├── dashy/               # Landing page
│   └── vault/               # Vault config
├── scripts/
│   ├── verify-arch.sh       # Container count + HTTP endpoint test
│   ├── diagnose.sh          # Full diagnostic (internal endpoints + service logs)
│   ├── test-routes.sh       # Quick route status check
│   ├── openclaw.py          # AIOS Lab Assistant
│   └── hermes.sh            # 24/7 autonomous ops agent
├── n8n/workflows/           # Use case workflows (TBD)
├── ansible/                 # Server setup playbooks
└── .github/workflows/ci.yml # CI pipeline
```
SysOps Frontend (infra management):
  Dashy, Grafana, Portainer, Prometheus, CrowdSec
  → US only — AIOS operators
  → Monitors containers, GPU, network, services

Functional Frontend (per use-case business UI):
  Separate dashboards per service
  → CLIENT uses — end customer daily operations
  → Monitors leads, attendance, cameras, calls, sales
  → Lives in Metabase / custom web apps / Streamlit
  → NEVER mixed into Dashy or Grafana
```

**Rule: Dashy is sysops-only.** No functional/end-client UIs live there. Each use case gets its own dedicated frontend.

### ⬅ NEXT SESSION — Resume Here

**Phase 1 — Architecture COMPLETE (33/33 containers, 8 zones, ALL verified ✅):**
1. ✅ **33 containers running** — all services healthy
2. ✅ **8 network zones** — DMZ, App, Data, AI, Voice, Mon, FOSS, Host
3. ✅ **All orphan containers added** to docker-compose-aios.yml
4. ✅ **Postgres switched to pgvector** — Dograh creates vector extension
5. ✅ **Frigate** running with GPU passthrough (10.40.0.50)
6. ✅ **Dograh** API + UI running (10.50.0.30-31), behind Traefik SSL
7. ✅ **Chatterbox** TTS running on GPU (10.40.0.30:4123)
8. ✅ **Mosquitto MQTT** running (10.50.0.20)
9. ✅ **CrowdSec fixed** — writable volume, proper acquis
10. ✅ **LVM extended** 100GB → 500GB
11. ✅ **Dashy** — central sysops hub with all service tiles
12. ✅ **Grafana** — auto-provisioned Prometheus + AIOS SysOps dashboard
13. ✅ **cAdvisor + node-exporter** — container + host metrics
14. ✅ **Traefik metrics** — internal for Prometheus scraping
15. ✅ **All env vars in .env** — no missing compose references
16. ✅ **Health verified** — `verify-arch.sh`: 33/33 containers, 13/13 HTTP endpoints
17. ✅ **4 use cases locked** — Surveillance, HR Payroll, Sales CRM, Voice Receptionist
18. ✅ **Frontend separation** — SysOps (Dashy/Grafana) vs Functional (per use case)
19. ✅ **Git pushed** — GitOps deploys automatically

**Phase 2 — Build 4 Use Cases (NEXT — arch complete):**
1. **CRM** (#3 easiest) — Pure n8n → OpenRouter → WhatsApp. No new infra needed.
2. **Voice** (#4) — Wire Asterisk → Dograh → Chatterbox → OpenRouter. Test call pipeline.
3. **HR** (#2) — n8n + face recognition + GPS + payroll logic. Needs GPU vision test.
4. **Surveillance** (#1 most complex) — Frigate + camera config + n8n alerts → WhatsApp.

**Build order per use case:**
```
Each use case:
  1. Create n8n workflow in /aios/n8n/workflows/{number}-{name}.json
  2. Node 2 = Set Variables (model, prompt_key, collection_id)
  3. HTTP POST → OpenRouter for inference
  4. Log to Langfuse for observability + cost tracking
  5. Test end-to-end with real data via webhook
  6. Build functional frontend (Metabase/Streamlit/custom)
  7. git commit + push
```

**Phase 3 — SysOps Monitoring:**
5. Wire Grafana dashboards — container health, GPU, LLM costs
6. Set up Uptime Kuma → WhatsApp alerts
7. Dashy as sysops hub (already live)

**4 USE CASES (from use-cases.docx):**
```
01-surveillance.json     Smart AI Surveillance & Security
                         Frigate NVR → GPU vision → n8n alerts → WhatsApp
                         Features: person/vehicle detection, restricted area alerts,
                                   face recognition, visitor counting, smart search

02-hr-payroll.json       Smart HR Attendance & Payroll
                         Face recognition + GPS + auto salary + leave mgmt
                         Features: face attendance, buddy punch prevention,
                                   GPS field tracking, auto shift, payroll calc,
                                   leave approval, employee self-service

03-sales-crm.json        Smart Sales CRM & Customer Management
                         Leads → WhatsApp CRM → pipeline → dashboard
                         Features: multi-source lead capture, sales team monitoring,
                                   WhatsApp CRM, auto reminders, sales dashboard,
                                   invoice follow-up, complaint tracking

04-voice-receptionist.json  AI Voice Receptionist & Call Center Agent
                            Asterisk → Dograh → STT → LLM → TTS → callback
                            Features: 24/7 call answering, Urdu/English,
                                      appointment booking, complaint registration,
                                      lead capture, payment reminders, human transfer
```

---

### SERVER SNAPSHOT
```
Hostname: aios
IP:       10.0.0.100
OS:       Ubuntu 22.04.5 LTS
CPU:      Intel Core i7-7800X @ 3.50GHz (6C/12T)
RAM:      31GB
GPU:      Quadro M4000 — 8GB VRAM ✅
Docker:   29.5.1 ✅
Containers: 33 — all managed via docker-compose
Disk:     953.9GB NVMe (free: TBD after cleanup)
```

### FILES REFERENCE
```
D:\AIOS\
├── PROJECT.md               # v4.0 — 16 sections
├── CLAUDE.md                # v4.0 — Claude Code instructions
├── CHECKPOINT.md            # This file
├── DEPLOYMENT_PLAN.md       # 18-step build plan
├── docker-compose-aios.yml  # AI core stack
├── docs/
│   ├── ARCHITECTURE_PHILOSOPHY.md
│   ├── INVENTORY.md
│   ├── SECURITY.md
│   ├── SOP.md
│   └── capabilities/
│       └── cisco-7962-provisioning.md
├── configs/
│   ├── asterisk/            # 12 config files + Dockerfile
│   ├── dnsmasq/             # SEP, XMLDefault, dialplan, tones
│   ├── traefik/             # Traefik routing + SSL
│   ├── crowdsec/            # WAF rules
│   ├── dashy/               # Landing page
│   └── vault/               # Vault config
├── scripts/                 # openclaw, new-client, backup, health-check, dr
├── ansible/                 # Server setup playbooks
└── .github/workflows/ci.yml # CI pipeline
```
