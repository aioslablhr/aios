# AIOS — COMPLETE ARCHITECTURE (CLEAR PICTURE)

## Two Layers:
## Layer 1: AI Infrastructure (engine room) — 7 Docker zones, GPU, security, voice
## Layer 2: AI Transformation (product) — 4 AI Digital Employees running on infra

---

## 1. WHAT WE BUILD VS WHAT WE DEPLOY

### WE BUILD (custom code — ~9 things total)

**AIOS Infrastructure Layer scripts:**
| # | What | Language | Lines | Location |
|---|------|----------|-------|----------|
| 1 | **health-check.py** | Python | ~200 | `/aios/scripts/health-check.py` |
| 2 | **backup.py** | Python | ~300 | `/aios/scripts/backup.py` |
| 3 | **disaster-recovery.py** | Python | ~300 | `/aios/scripts/disaster-recovery.py` |
| 4 | **AIOS wiki compiler** | Python | ~200 | Not written yet |

**AI Transformation Layer — use case workflows:**
| # | What | Format | Lines | Location |
|---|------|--------|-------|----------|
| 5 | **01-surveillance.json** | n8n JSON | ~500 | `/aios/n8n/workflows/` |
| 6 | **02-hr-payroll.json** | n8n JSON | ~500 | `/aios/n8n/workflows/` |
| 7 | **03-sales-crm.json** | n8n JSON | ~500 | `/aios/n8n/workflows/` |
| 8 | **04-voice-receptionist.json** | n8n JSON | ~500 | `/aios/n8n/workflows/` |
| 9 | **Functional frontends** | Streamlit/Metabase | varies | Per use case |

That's it. Everything else is **off-the-shelf Docker containers** we configure.

### WE DEPLOY (off-the-shelf apps — just configure)
| Category | Apps | Config We Write |
|----------|------|-----------------|
| Data | PostgreSQL, Redis, MinIO, Qdrant, ClickHouse | compose + env vars |
| Security | Traefik, CrowdSec, Keycloak, Vault, WireGuard | compose + config files |
| AI | Ollama, Langfuse, Bifrost, Chatterbox | compose + model configs |
| Voice | Asterisk, Dograh | compose + dialplan + SIP config |
| Orchestration | n8n + 2 workers, Flowise | compose + workflow templates |
| Monitoring | Grafana, Prometheus, Loki, Portainer, Uptime Kuma, Dashy, Dozzle | compose + dashboard JSON |
| FOSS Apps | Metabase, ERPNext, Odoo, Twenty CRM, Calcom, Paperless-ngx, Docuseal, Rocket.Chat | compose + env vars |
| Dev Tools | GitOps Agent, Hermes, nvidia-smi-exporter | compose + shell scripts |

### WE CONSUME (cloud services)
| Service | What For | Cost |
|---------|----------|------|
| **OpenRouter** | ALL LLM inference (free tier + paid) | Free-$20/mo for dev |
| Cloudflare | DNS, tunnel, DDoS, SSL | Free |
| WhatsApp API | Meta Business API for messaging | Usage-based |
| SIP Trunk | PSTN calling (future) | Per minute |

---

## 2. PHYSICAL TOPOLOGY — HOW THE WIRES GO

```
                   INTERNET (100Mbps Fiber)
                          │
                    [Huawei ONT]
                  10.0.0.1 (gateway)
                   ┌──────┴──────┐
                   │              │
            [Server aios]    [Dev PC]
             10.0.0.100      10.0.0.13
                   │
     ┌─────────────┼──────────────┬──────────────┐
     │             │              │              │
  [Switch/LAN]  [IP Cams]   [IP Phones]    [IoT Devices]
     │          RTSP:554     SIP:5060      MQTT:1883
     │             │              │              │
  [WiFi AP]  [Hikvision/   [Cisco 7962]   [Temp/
  for other   Dahua cams]   Ext 9000       Humidity
  devices                                  sensors]
```

### Physical connections summary:
- **Server** — 1 Ethernet cable to ONT (internet) + 1 cable to LAN switch
- **IP Cams** — Ethernet to switch, RTSP stream to server port 8554
- **IP Phones** — Ethernet to switch, SIP/TFTP to server
- **IoT** — WiFi to AP, MQTT to server port 1883
- **Dev PC** — Ethernet to switch (or WiFi)
- **Everything is on 10.0.0.0/24 LAN** — no device reaches internet directly

---

## 3. LOGICAL ARCHITECTURE — 7 ZONES

### Zone Dependencies (strict order)
```
DMZ → App → Data → AI → Voice → Mon → FOSS
│       │      │     │      │      │      │
│       │      │     │      │      │      └── Client apps
│       │      │     │      │      └──────── Monitoring
│       │      │     │      └─────────────── Voice pipeline
│       │      │     └────────────────────── AI inference
│       │      └──────────────────────────── Data stores
│       └─────────────────────────────────── App logic
└─────────────────────────────────────────── Public face
```

### Zone 1 — DMZ (10.10.0.0/24)
Only zone exposed to internet. Port 443 only.
```
Cloudflare Tunnel ─→ Traefik (reverse proxy)
                           └→ CrowdSec (WAF)
                                └→ Keycloak (auth) in App zone
```
Running: Traefik, CrowdSec

### Zone 2 — App (10.20.0.0/24)
ALL business logic lives here.
```
Running: Keycloak, Vault, GitOps, Hermes
Planned: n8n, n8n-workers, Flowise, WireGuard
```
Core function: Orchestrates everything. n8n is the brain — every request goes through n8n workflows.

### Zone 3 — Data (10.30.0.0/24)
INTERNAL:TRUE — NO internet access ever.
```
Running: PostgreSQL, Qdrant, Redis, MinIO, Langfuse, ClickHouse
```
Core function: All data stays here. Cannot phone home.

### Zone 4 — AI (10.40.0.0/24)
GPU zone (Quadro M4000 passthrough).
```
Running: Ollama, Bifrost, Chatterbox (TTS GPU), Frigate (GPU YOLO)
Planned: Kokoro (TTS CPU fallback)
```
GPU jobs: embeddings (nomic), vision (LLaVA), TTS (Chatterbox), STT (Whisper in Dograh), object detection (Frigate YOLO).
Kokoro TTS runs on CPU — fallback when GPU busy. Dograh auto-selects between both TTS engines.

### Zone 5 — Voice (10.50.0.0/24)
```
Running: Dograh API, Dograh UI, Mosquitto
Planned: Kokoro TTS (10.40.0.31 — CPU fallback)
```
Dograh orchestrates: Whisper STT → n8n → LLM → TTS (Chatterbox GPU primary, Kokoro CPU fallback)

### Zone 6 — Monitoring (10.60.0.0/24)
```
Running: nothing yet
Planned: Grafana, Prometheus, Loki, Portainer, Uptime Kuma, Dashy, Dozzle, nvidia-smi-exporter
```
Core dashboard for admin team.

### Zone 7 — FOSS (10.70.0.0/24)
```
Running: nothing yet
Planned: Metabase, ERPNext, Odoo, Twenty CRM, Calcom, Paperless-ngx, Docuseal, Rocket.Chat
```
Client-facing business apps. Metabase is the PRIMARY client dashboard.

---

## 4. DATA FLOWS — COMPLETE PATH OF EVERY REQUEST

### 4A. WhatsApp Message
```
Phone → Meta → Cloudflare → Traefik → CrowdSec → n8n webhook
  → n8n workflow (use-case specific)
    → Node 2: Set Variables (workflow_id, model, prompt_key)
    → IF/SWITCH routing
      → OpenRouter API → LLM response
    → Langfuse log: prompt + response + cost
    → Supabase log: conversation history
  → Meta WhatsApp API → response to client
Time: <3 seconds
```

### 4B. Voice Call
```
Caller dials → SIP Trunk → Asterisk (host:5060)
  → Dograh (10.50.0.30) — voice agent orchestration
    → Whisper STT (GPU) — transcribes speech to text
    → n8n webhook → same path as WhatsApp above
    → OpenRouter → LLM response
    → Dograh auto-selects TTS:
        Chatterbox (GPU, high quality) or Kokoro (CPU, faster fallback)
  → Audio back through Asterisk → caller hears AI voice
```

### 4C. IP Camera Event
```
Camera (RTSP) → go2rtc (10.20.0.91) → Frigate (10.20.0.90, GPU)
  → YOLO detects object (person/vehicle)
  → LLaVA describes scene: "delivery driver at front door"
  → MQTT publish (10.50.0.20:1883)
  → n8n subscribes → LLM decides action
  → WhatsApp alert to client owner
  → Supabase log
```

### 4D. Document Upload → Knowledge
```
User uploads PDF/doc → Supabase Storage
  → n8n ingestion workflow
    → nomic-embed-text → vector embeddings
    → Qdrant stores in knowledge collection
    → Agent has instant access
```

---

## 5. CURRENT STATE VS TARGET (WHERE THE CONFUSION IS)

Currently running (15 containers):
```
✓ Data:  PostgreSQL, Qdrant, Redis, MinIO
✓ AI:    Ollama (Mistral 7B + Qwen 2.5 7B + Llama 3.2 3B), Bifrost (with OpenRouter)
✓ Mon:   ClickHouse, Langfuse
✓ App:   Keycloak, Vault, GitOps, Hermes
✓ DMZ:   Traefik, CrowdSec
✓ Voice: Asterisk (host net)
```

Still NEED to deploy (Infrastructure Layer — most deployed, updating):
```
⬜ All 4 use case workflows ← Transformation Layer — being built
⬜ n8n + 2 workers          ← Brain of the system — running
⬜ WireGuard                ← Remote access
⬜ Chatterbox               ← TTS on GPU — running
⬜ Dograh                   ← Voice agent orchestration — running
⬜ Frigate + go2rtc        ← Camera pipeline — running
⬜ Prometheus/Grafana       ← Monitoring — running
⬜ Portainer/Dashy          ← Management UI — running
```

Architecture decisions made (docs say one thing, running says another):
```
DOCS SAY:       RUNNING:        REALITY:
────────────────────────────────────────────────
No local LLMs   Mistral + Qwen   We haven't cleaned up yet
Direct OpenRouter Bifrost routes  We haven't rewired yet
Dograh ready    Not deployed     Need to deploy
Chatterbox ready Not deployed    Need to deploy
```

---

## 7. SUMMARY — WHAT AIOS ACTUALLY IS

Two Layers, one server:

**Layer 1 — AI Infrastructure (the engine room)**
A server (10.0.0.100) running ~40 Docker containers:
Security (Cloudflare → Traefik → CrowdSec → Keycloak → Vault)
Data (PostgreSQL, Qdrant, Redis, MinIO, ClickHouse, Langfuse)
Inference (Bifrost → OpenRouter, Whisper STT, Chatterbox TTS on GPU)
**Voice Pipeline** — Asterisk → Dograh → Whisper → n8n → Bifrost → LLM → TTS (Chatterbox GPU or Kokoro CPU, Dograh auto-selects)
Monitoring (Grafana, Prometheus, Loki, Portainer, Dashy)

**Layer 2 — AI Transformation (the product — running on Layer 1)**
4 AI Digital Employees replacing manual business processes:
1. **Sales CRM** — WhatsApp leads → AI conversation → Twenty CRM pipeline
2. **Voice Receptionist** — SIP calls → AI conversation → booking
3. **HR Payroll** — Face recognition + GPS → attendance + salary
4. **Surveillance** — Cameras → Frigate GPU detection → WhatsApp alerts

**We write:** ~5 Python scripts + 4 n8n workflow JSONs. Everything else is off-the-shelf Docker containers we configure.
