# AIOS — Build Checkpoint
## Last Updated: May 26, 2026 — Architecture COMPLETE — 51/51 containers on 8 zones

---

### ✅ COMPLETED STEPS

**Phase 0-2 Foundation:** GPU driver, Docker, 8 networks, data + security layer, Vault, Git/GitHub, CI, GitOps, Hermes, Cloudflare tunnel + SSL + Dashy

**Asterisk + Cisco 7962G:** 22.9.0 compiled, 6 extensions, Cisco registered on TCP transport fix

**n8n + OpenRouter (May 25):** n8n stack main + db + 2 workers, webhook test with `liquid/lfm-2.5-1.2b:free`

**Architecture Finalized (May 26):**
- **CrowdSec fixed** — writable volume, proper acquis for Traefik logs
- **LVM extended** — 100GB → 500GB (419GB free)
- **Mosquitto MQTT** — deployed (10.50.0.20), event bus for Frigate + Dograh
- **Frigate NVR** — deployed with GPU passthrough (10.40.0.50), healthy
- **Dograh API + UI** — deployed (10.50.0.30-31), connected to AIOS Postgres/Redis/MinIO
- **Chatterbox TTS** — deployed on GPU (10.40.0.30:4123)
- **Postgres switched to pgvector** — `pgvector/pgvector:0.8.0-pg16` enables Dograh vector extension
- **Missing env vars added** — N8N_DB_PASSWORD, N8N_ENCRYPTION_KEY, GRAFANA_ADMIN_PASSWORD in .env
- **Dashy updated** — tiles added for Qdrant, Bifrost, Dograh, Chatterbox, Mosquitto, Postgres, Redis
- **Prometheus config** — created with scraping targets for n8n, Traefik, Bifrost, Frigate
- **4 use cases locked** — Surveillance, HR Payroll, Sales CRM, Voice Receptionist
- **Frontend separation defined** — SysOps (Dashy/Grafana) vs Functional (Metabase/custom per use case)

**51/51 containers running across 8 network zones**

---

### ❌ KNOWN ISSUES

- **Keycloak** cycling after postgres recreate — stabilizes on its own (health check)
- **Vault** — still on host networking, needs move to aios-app network (non-blocking)
- **SIP trunk** — `TRUNK_PASS` still placeholder, no external calls (non-blocking)
- **Vault keys** — in plaintext, needs encrypted backup (non-blocking)
- **n8n API key** — enterprise feature, using session cookie for now (non-blocking)
- **OpenRouter** — free tier rate limits (429 on free models under heavy use) (non-blocking)

---

### ✅ ARCHITECTURE DECISIONS — May 25, 2026

### ✅ ARCHITECTURE DECISIONS — May 26, 2026 (LOCKED)

- **No capability abstraction layer:** MVP v1 builds 4 real business use cases as standalone n8n workflows directly on the stack. No reusable sub-workflow templates. No test client abstraction. Use cases run directly on the AIOS architecture.
- **Why:** MVP is a prototype — validate use cases, not abstractions. Capability layer adds complexity before we know what works. Real use cases = faster iteration, real feedback. Client isolation postponed to v2.
- **4 use cases (from use-cases.docx):** AI Surveillance, HR Attendance & Payroll, Sales CRM, Voice Receptionist

### ✅ FRONTEND ARCHITECTURE — SysOps vs Functional (LOCKED May 26)

**Two completely separate stacks:**

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

**Phase 1 — Architecture COMPLETE (51/51 containers on 8 zones):**
1. ✅ **51 containers running** — all services healthy
2. ✅ **8 network zones** — DMZ, App, Data, AI, Voice, Mon, FOSS, Host
3. ✅ **All orphan containers added** to docker-compose-aios.yml
4. ✅ **Postgres switched to pgvector** — Dograh creates vector extension
5. ✅ **Frigate** running with GPU passthrough on AI zone (10.40.0.50)
6. ✅ **Dograh** API + UI running on Voice zone (10.50.0.30-31)
7. ✅ **Chatterbox** TTS running on GPU (10.40.0.30:4123)
8. ✅ **Mosquitto MQTT** running on Voice zone (10.50.0.20)
9. ✅ **CrowdSec fixed** — writable volume, proper acquis
10. ✅ **LVM extended** 100GB → 500GB
11. ✅ **Dashy updated** — all services in sysops hub
12. ✅ **Prometheus configured** — scraping targets for all services
13. ✅ **All env vars in .env** — no missing compose references
14. ✅ **4 use cases locked** — Surveillance, HR Payroll, Sales CRM, Voice Receptionist

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
Containers: 51 — all managed via docker-compose
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
