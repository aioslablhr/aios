# AIOS — AI Operating System
## Master Reference for OpenCode · Lahore AI Lab · 2026

---

## 1. WHAT IS AIOS

Production-grade self-hosted hybrid AI platform — an AgentOS.
Runs AI agents as digital employees for SMBs across Pakistan and UAE.

```
v1 (now):   Single tenant. One shared platform. Multiple use cases on top.
            5 full business systems: HR+Attendance, Call Centre,
            Customer Experience, Finance, Marketing+Sales
v2 (later): Multi-tenant per client. K3s auto-scaling. LLM Wiki.
            Central unified dashboard. Arize Phoenix.
```

Business:
```
Markets:  Pakistan (Lahore) → UAE → USA/Canada (white-label)
Pricing:  Tier 1 PKR 12-18K/mo | Tier 2 PKR 45-65K/mo | Tier 3 PKR 130-200K/mo
Stack:    40+ microservices | 15 infrastructure layers | 2 GPU servers
```

---

## 2. PHYSICAL MACHINES — 2 ONLY

### WS1 — 192.168.1.10 / WireGuard 10.70.0.1
```
OS:      Ubuntu 24.04 LTS
GPU:     RTX 4090 24GB
RAM:     64GB DDR5
Storage: 2TB NVMe + 4TB HDD
Public:  YES — port 443 only via Cloudflare + OPNsense + Traefik
```

WS1 internal layout:
```
KVM Layer:      OPNsense VM (FreeBSD, 2GB) + Issabel VM (AlmaLinux, 4GB)
Docker Layer A: FOSS non-AI apps (docker-compose-apps.yml)
Docker Layer B: AI core services (docker-compose-aios.yml)
Installed:      OpenCode (Desktop+CLI), OpenClaw, Ansible, Hermes Agent
```

### Inference Server — 192.168.1.20 / WireGuard 10.70.0.2
```
OS:      Ubuntu 24.04 LTS bare metal
GPU:     2× RTX 3090 24GB (RTX#1: Llama 70B+Mistral | RTX#2: Qwen 72B+Frigate)
RAM:     128GB DDR4
Storage: 4TB NVMe + 8TB HDD + NAS 4-bay 8TB
Public:  NEVER — WireGuard tunnel only
Docker:  vLLM, Frigate, LLaVA, YOLOv9, go2rtc, nvidia-smi-exporter
```

---

## 3. AIOS ARCHITECTURE — 15 LAYERS

### LAYER 0 — PHYSICAL HARDWARE
```
WS1: RTX 4090 | 64GB DDR5 | 2TB NVMe
Inference Server: 2× RTX 3090 | 128GB RAM | 4TB NVMe | NAS 8TB
```

### LAYER 1 — HYPERVISOR (WS1 KVM)
```
OPNsense VM  FreeBSD   2GB  20GB  Network firewall, IDS/IPS Suricata,
                                   WireGuard VPN, VLAN, NAT, DNS
Issabel VM   AlmaLinux 4GB  80GB  UC platform, call centre GUI,
                                   IVR, recordings, SIP trunked to Asterisk
```

### LAYER 2 — SECURITY (5 sub-layers in sequence)
```
1. Cloudflare      Cloud        DDoS, SSL, CDN, edge protection
2. OPNsense        WS1 KVM      Network firewall, IDS/IPS, WireGuard
3. Traefik         WS1 Docker B Reverse proxy, HTTPS termination
4. CrowdSec        WS1 Docker B WAF, IP reputation, rate limiting
5. Keycloak+Vault  WS1 Docker B Identity, RBAC, OAuth2, secrets
```

API Gateways:
```
Traefik  → all HTTP/HTTPS traffic into AIOS
Bifrost  → all LLM API calls (routing, caching, budget, failover)
```

### LAYER 3 — INPUT CHANNELS
```
Voice calls    Asterisk SIP + Dograh
WhatsApp       Meta WhatsApp Business API → n8n webhook
Web chat       React widget → n8n webhook
Email          IMAP/SMTP → n8n
SMS            Twilio
IP Cameras     RTSP → go2rtc → Frigate
Documents      Supabase Storage → n8n
REST API       n8n webhook nodes
```

### LAYER 4 — AI GATEWAY & LLM INTELLIGENCE
```
Bifrost     WS1 Docker B (10.40.0.10:4000)
            ALL LLM calls go here ONLY — never direct API
            Semantic caching, per-client keys, budget controls,
            prompt injection detection, automatic failover, MCP support

LOCAL MODELS (via vLLM on Inference Server):
  Llama 3.1 70B Q4  RTX 3090 #1  General reasoning, agent tasks
  Mistral 7B         RTX 3090 #1  Fast intent detection (cheapest)
  Qwen 2.5 72B       RTX 3090 #2  Arabic + Urdu (best multilingual)
  LLaVA 7B           RTX 3090 #2  Vision — invoices, camera snapshots

CLOUD LLMs (via Bifrost only):
  Claude 4 Sonnet  Anthropic   Complex reasoning (5-10% of calls)
  GPT-4o           OpenAI      Vision fallback, structured extraction
  Gemini 2.0       Google      Multimodal fallback
  NVIDIA NIM API   NVIDIA      Free 1K credits (build.nvidia.com)
  LiteLLM          WS1         DEV/PROTO ONLY — not in production

Bifrost Routing:
  Simple/FAQ:      Mistral 7B (local — free)
  Urdu/Arabic:     Qwen 72B (local — free)
  General:         Llama 70B (local — free)
  Complex/legal:   Claude 4 Sonnet (API)
  Vision:          LLaVA (local) → GPT-4o (fallback)
  Cached queries:  Bifrost semantic cache (zero LLM call)
```

Prompt Registry:
```
Langfuse   All agent prompts versioned + stored
           Agents pull at runtime — change once, all update
nomic-embed-text + LlamaIndex  RAG pipeline (chunking + embedding)
```

### LAYER 5 — VOICE AI (FINAL LOCKED)
```
Dograh     WS1 Docker B (10.50.0.11:3010)
           FOSS voice agent platform — replaces Retell AI + Vapi
           MCP-native, self-hosted, zero per-minute cost
           BSD-2 license | dograh.com

Asterisk   WS1 Docker B (10.50.0.10)  Core SIP engine
Issabel    WS1 KVM VM                  UC management GUI
Deepgram   Cloud (optional)            Best Urdu STT ($0.0077/min)
ElevenLabs Cloud (optional)            Natural voice TTS ($22/mo)

Voice pipeline options:
  Full local (free):    Asterisk → Dograh → Whisper → Bifrost → Kokoro/Chatterbox
  Hybrid (best Urdu):   Asterisk → Dograh → Deepgram → Bifrost → ElevenLabs

TTS selection:
  Urdu:    ElevenLabs (cloud, best) or Meta MMS (local, free)
  English: Chatterbox-Turbo (self-hosted, beats ElevenLabs in tests)
  Fast:    Kokoro (210x real-time, Apache 2.0, English only)
  NOTE:    Kokoro + Chatterbox = English only. Urdu needs ElevenLabs or MMS.
```

### LAYER 6 — VISUAL AI
```
Frigate 0.17  Inference Server  Object detection + face recognition
YOLOv9 TRT    RTX 3090 #2       GPU-accelerated detection model
LLaVA 7B      RTX 3090 #2       Natural language event descriptions
go2rtc        Inference Server  IP camera RTSP stream management
MQTT          WS1 Docker B      Frigate event → n8n workflow trigger

Pipeline: IP Camera → go2rtc → Frigate → YOLOv9 → LLaVA → MQTT → n8n
```

### LAYER 7 — MEMORY (4 sub-layers)
```
Qdrant    WS1 Docker B (10.30.0.20:6333)
          Vector DB — RAG knowledge base per use case
          Static — read-only knowledge (FAQs, SOPs, policies)

Mem0      WS1 Docker B
          Persistent user/customer memory across ALL sessions
          Connects to Supabase as backend
          Dynamic — learns from every interaction

Redis     WS1 Docker B (10.30.0.30:6379)
          Session memory — current conversation only
          n8n queue mode backend

LLM Wiki  Phase 2 — agent self-learning
          cap-wiki-write.json + cap-wiki-consolidate.json
          Agent writes patterns learned from interactions back to Qdrant
```

### LAYER 8 — AGENT FRAMEWORK & ORCHESTRATION
```
n8n (queue mode)     WS1 Docker B (10.20.0.10:5678)
                     Master orchestrator — ALL workflows, ALL triggers
                     1,400+ integrations, Redis queue, workers ×2
                     80% of all agent logic runs here

n8n AI Agent node    Inside n8n workflows — simple in-workflow reasoning
                     LLM thinks → calls tools → returns to workflow
                     No separate Python file needed

FastAPI+LangGraph    WS1 Docker B — ports 8001-8005
base template:       wassim249/fastapi-langgraph-agent-production-ready-template
                     ALREADY HAS: FastAPI, LangGraph loop, Mem0+pgvector,
                     Langfuse tracing, Prometheus+Grafana, rate limiting,
                     Docker ready, structured logging
                     CHANGED FOR AIOS: Bifrost instead of OpenAI,
                     Langfuse instead of LangSmith, Keycloak auth
                     USE FOR: complex reasoning agents (20% of tasks)

Domain agents (from base template):
  hr_agent.py          port 8001  HR reasoning, ERPNext HR tools
  finance_agent.py     port 8002  Invoice validation, accounting
  legal_agent.py       port 8003  Contract review, Claude 4 Sonnet
  sales_agent.py       port 8004  Lead research, CRM update
  operations_agent.py  port 8005  Supply chain, inventory reasoning

CrewAI               WS1 Docker B
                     Multi-specialist agent teams for complex tasks
                     USE FOR: invoice crew, lead enrichment, legal review
                     Called by n8n via HTTP when task needs specialists

LangGraph            Inside domain agents (agent.py framework)
                     Stateful graph-based reasoning with loops
                     USE FOR: complex multi-step with conditional paths

Tool selection rule:
  n8n only       → simple trigger + steps (80% of workflows)
  n8n AI Agent   → simple in-workflow LLM reasoning
  agent.py       → complex domain reasoning (called by n8n via HTTP)
  CrewAI         → multi-specialist parallel tasks
  LangChain      → custom Python logic (last resort only)
```

Agent directory structure:
```
/aios/agents/
├── /base/              ← wassim249 template (cloned from GitHub)
├── /tools/
│   ├── erpnext_tools.py
│   ├── qdrant_tools.py
│   ├── whatsapp_tools.py
│   └── vision_tools.py
├── hr_agent.py         port 8001
├── finance_agent.py    port 8002
├── legal_agent.py      port 8003
├── sales_agent.py      port 8004
└── operations_agent.py port 8005
```

### LAYER 9 — TOOLS & INTEGRATIONS
```
Central MCP Server    WS1 Docker B
                      All tools defined ONCE — used by ALL agents
                      Tools: ERPNext, Twenty CRM, Calcom, WhatsApp,
                      Gmail/SES, Google Calendar, Qdrant, Supabase,
                      Paperless-ngx, web_search, file_tool, payment_tool
                      Add one tool → available to ALL agents instantly

FOSS Apps (Docker Layer A):
  Odoo            Full ERP
  ERPNext/Frappe  Full ERP + Hospital/Hotel/Restaurant/Manufacturing/LMS
  Twenty CRM      Modern Salesforce alternative
  SuiteCRM        Enterprise CRM
  Calcom          Booking + scheduling
  Paperless-ngx   Document management + OCR
  Docuseal        FOSS e-signing
  Planka          Project management
  Rocket.Chat     Team communication
  Frappe LMS      Learning management
  GnuCash         Lightweight accounting
  Metabase        Client-facing dashboards

External Integrations (via n8n + Central MCP):
  WhatsApp Business API, Twilio, Google Calendar, Microsoft 365
  JazzCash/EasyPaisa, Stripe, Facebook/Instagram API
  ZKTeco SDK (biometric attendance), Apollo.io (B2B leads)
```

### LAYER 10 — AGENT GOVERNANCE
```
Paperclip     WS1 Docker B
              AI company OS — manages ALL agents
              Connects to Bifrost for LLM routing
              v1: 3 internal companies (Infrastructure, Product, Founder)
              v2: + one company per client

Mission Control  WS1 Docker B (10.60.0.90:3000)
                 Agent fleet operations dashboard (mc.builderz.dev)
                 Tasks, costs, status, fleet ops
                 Native adapters: OpenClaw, CrewAI, LangGraph, Claude Code

Langfuse      WS1 Docker B (10.60.0.10:3000)
              Prompt registry + LLM observability
              Every LLM call: cost, latency, quality score, per-use-case

OpenTelemetry WS1 — distributed tracing across all tiers
```

### LAYER 11 — INTERNAL LAB INTELLIGENCE
```
OpenCode         WS1 (SSH)     Primary AI dev tool — builds everything
                               Reads AGENTS.md automatically every session
                               Desktop SSH = full native tools (preferred)
                               Points to Bifrost for all LLM calls

Hermes Agent     WS1 installed  Autonomous 24/7 DevOps
                               YOU talk to Hermes via Telegram
                               Spawns parallel subagents for complex tasks
                               Monitors, maintains, recovers AIOS
                               Connects to Bifrost (local Qwen 72B)
                               Connects to Central MCP for AIOS tools
                               Dashboard at port 9119

OpenClaw         WS1 installed  Personal AI assistant via WhatsApp/Telegram
                               Multi-agent support (Inky, Pinky etc.)
                               Connects to Bifrost for LLM
                               Connects to Central MCP for tools
```

### LAYER 12 — DATA & STORAGE
```
Supabase    WS1 Docker B (10.30.0.10:8000)  Operational DB (Postgres)
Qdrant      WS1 Docker B (10.30.0.20:6333)  Vector DB + RAG
Mem0        WS1 Docker B                     Persistent agent memory
Redis       WS1 Docker B (10.30.0.30:6379)  Queue + session cache
MinIO       WS1 Docker B (10.30.0.40:9000)  Object storage (S3-compatible)
NAS 4-bay   Inference Server rack            Model files, datasets, backups
AWS S3      Cloud hybrid                     Nightly encrypted backup
```

Data zone (10.30.0.0/24) has internal:true — NO internet access EVER.

### LAYER 13 — DASHBOARDS
```
SysOps (your team):
  Dashy           Navigation homepage — all tools linked, live status
  Grafana         Single pane of glass — infra + LLM + business metrics
  Mission Control Agent fleet dashboard
  Langfuse        LLM observability
  Portainer       Container management
  Uptime Kuma     Service uptime + WhatsApp alerts
  Dozzle          Real-time Docker logs
  Hermes dash     DevOps agent (port 9119)
  OpenClaw dash   Personal agent UI

Functional (use cases):
  Metabase        Business KPIs per use case
  React portal    Custom white-label portal
  n8n agents      Auto daily/weekly reports → WhatsApp/email
```

### LAYER 14 — SYSOPS & CI/CD
```
ArgoCD          WS1 Docker B    GitOps CD — push → auto-deploy
GitHub Actions  WS1 Docker B    CI — validates every push
Ansible         WS1 installed   Server setup + disaster recovery
Watchtower      WS1 Docker B    Auto-updates containers
Trivy           WS1 Docker B    Container security scanning
Prometheus      WS1 Docker B    Metrics collection
Loki            WS1 Docker B    Log aggregation
Automated backup Both + cloud   Nightly NAS + S3 (AES-256 encrypted)
```

### LAYER 15 — HYBRID CLOUD
```
ON-PREMISE (primary):
  All AI workloads, all data, all voice, all inference

AWS HYBRID ($200 credit):
  S3              Nightly backup                5GB free
  CloudFront      CDN for dashboards/portals    1TB/mo free
  SES             All transactional emails       62K emails/mo free
  EC2 t2.micro    Overflow compute               750hrs/mo free
  Lambda          Serverless event routing       1M requests/mo free
  NOTE: Route 53 NOT used — Cloudflare handles all DNS

EXTERNAL APIs (via Bifrost):
  Anthropic Claude, OpenAI GPT-4o, Google Gemini
  Deepgram Nova 3, ElevenLabs, Meta WhatsApp, Twilio
  NVIDIA NIM (free 1K credits — build.nvidia.com)
```

---

## 4. DOCKER NETWORK ZONES (7 isolated)

```
10.10.0.0/24  DMZ          Traefik (.10), CrowdSec (.11) — internet facing only
10.20.0.0/24  Application  n8n (.10/.11/.12), Flowise (.20), Dify (.21),
                            OpenWebUI (.30), Keycloak (.40), Vault (.50),
                            Agents (.60-.65)
10.30.0.0/24  Data         Supabase (.10), Qdrant (.20), Redis (.30),
                            MinIO (.40) — internal:true, NO internet EVER
10.40.0.0/24  AI           Bifrost (.10), Ollama-dev (.20), LiteLLM-dev (.30)
10.50.0.0/24  Voice        Asterisk (.10), Dograh (.11), MQTT (.20)
10.60.0.0/24  Monitoring   Langfuse (.10), Prometheus (.20), Grafana (.30),
                            Loki (.40), Portainer (.50), Uptime Kuma (.60),
                            Dashy (.70), Dozzle (.80), Mission Control (.90)
10.70.0.0/24  Cross-machine WireGuard: WS1(.1) ↔ Inference Server(.2)
```

---

## 5. SERVICE PORTS QUICK REFERENCE

```
Bifrost:         10.40.0.10:4000   ← ALL LLM calls go here
vLLM:            10.70.0.2:8000    ← via WireGuard
n8n:             10.20.0.10:5678
Qdrant:          10.30.0.20:6333
Supabase:        10.30.0.10:8000
Redis:           10.30.0.30:6379
MinIO:           10.30.0.40:9000
Langfuse:        10.60.0.10:3000
Grafana:         10.60.0.30:3000
Portainer:       10.60.0.50:9000
Dashy:           10.60.0.70:80
Prometheus:      10.60.0.20:9090
Mission Control: 10.60.0.90:3000
Keycloak:        10.20.0.40:8080
Vault:           10.20.0.50:8200
Asterisk:        10.50.0.10 (SIP)
Dograh:          10.50.0.11:3010
MQTT:            10.50.0.20:1883
Hermes:          WS1:9119
hr_agent:        10.20.0.60:8001
finance_agent:   10.20.0.61:8002
legal_agent:     10.20.0.62:8003
sales_agent:     10.20.0.63:8004
ops_agent:       10.20.0.64:8005
Ollama:          10.40.0.20:11434 (dev only)
```

---

## 6. QA FRAMEWORK

```
Layer 1 — Golden datasets (before deploying any use case):
  50 test conversations per use case
  pytest against n8n webhook + agent.py endpoints
  Must pass 90%+ before any real user interaction

Layer 2 — CI gate (every git push):
  GitHub Actions: YAML validation + pytest + Trivy + latency check
  BLOCKS ArgoCD deployment if any test fails

Layer 3 — Production monitoring:
  Langfuse quality scores every LLM call
  Alert to Telegram/WhatsApp if:
    Error rate > 5% | Latency > 3s (WhatsApp) or > 1.5s (voice)
    Cost spike | Agent wrong 3 times in a row

Layer 4 — Regression (every prompt change):
  Langfuse A/B comparison old vs new prompt on golden dataset
  Blocks if quality drops

Latency targets:
  WhatsApp reply:      < 3 seconds
  Voice response:      < 1.5 seconds (Dograh local)
  FAQ cached:          < 1 second (Bifrost cache)
  Appointment booking: < 4 seconds
  Invoice processing:  < 10 seconds (LLaVA)
```

---

## 7. USE CASES — ON TOP OF AIOS (v1 single tenant)

v1 = one shared platform, multiple use cases, no isolation.
Each use case = n8n workflow + Qdrant collection + Langfuse prompt + optional agent.py

```
#  Use Case              n8n Workflow              agent.py Used?
─────────────────────────────────────────────────────────────────
1  HR + Attendance        hr-main.json             hr_agent.py (complex HR)
2  AI Call Centre         callcentre-main.json      None (Dograh handles voice)
3  Customer Experience    cx-main.json              None (n8n sufficient)
4  Finance + Accounting   finance-main.json         finance_agent.py (invoice crew)
5  Marketing + Sales      marketing-main.json       sales_agent.py (lead research)
```

3 product tiers:
```
Tier 1 Starter:    WhatsApp + Reputation + Basic CRM   PKR 12-18K/mo
Tier 2 Business:   All 5 use cases full                PKR 45-65K/mo
Tier 3 Enterprise: All + Supply Chain + Legal + Custom  PKR 130-200K/mo
```

See AIOS_USECASES.md for full technical specs per use case.

---

## 8. AGENT BUILDING — OVERPOWERED METHOD

```
You describe the agent → OpenCode builds it → You test → Done

OpenCode reads AGENTS.md automatically (knows full architecture)

TOOL SELECTION (OpenCode follows this):
  n8n only         → trigger + steps + integrations (80%)
  n8n AI Agent     → simple in-workflow LLM reasoning
  agent.py         → complex domain reasoning (called by n8n via HTTP)
  CrewAI           → multiple specialist agents on one task
  LangChain        → custom Python logic (last resort)

AGENT TYPES:
  n8n AI Agent node:  inside n8n, no separate file, visual
  agent.py:           standalone FastAPI + LangGraph, called via HTTP
  CrewAI crew:        multiple agent.py files coordinated
  OpenClaw agents:    pre-built personal assistant framework
  Hermes agent:       pre-built DevOps framework (YOU talk to this)
```

---

## 9. CRITICAL RULES — NEVER VIOLATE

```
1.  ALL LLM calls → Bifrost ONLY (http://10.40.0.10:4000)
2.  ALL voice → Dograh + Asterisk ONLY (never Retell AI or Vapi)
3.  NO hardcoded secrets — all from HashiCorp Vault
4.  Data zone (10.30.0.0/24) internal:true — never change
5.  Inference Server (192.168.1.20) NEVER public
6.  ALL LLM calls logged to Langfuse (cost tracking)
7.  ADD input + output guardrail nodes to every n8n workflow
8.  ADD Mem0 read at start + write at end of every agent
9.  COMMIT to Git before any production change
10. Kokoro + Chatterbox = English only — Urdu needs ElevenLabs or MMS
```

---

## 10. DIRECTORY STRUCTURE

```
/aios/
├── AGENTS.md                    ← OpenCode reads automatically
├── docker-compose-aios.yml      ← AI core (Layer B)
├── docker-compose-apps.yml      ← FOSS apps (Layer A)
├── .env.aios                    ← AI secrets from Vault
├── .env.apps                    ← App secrets from Vault
├── /agents/
│   ├── /base/                   ← wassim249 LangGraph template
│   ├── /tools/                  ← shared tool functions
│   ├── hr_agent.py              ← port 8001
│   ├── finance_agent.py         ← port 8002
│   ├── legal_agent.py           ← port 8003
│   ├── sales_agent.py           ← port 8004
│   └── operations_agent.py      ← port 8005
├── /ansible/
│   ├── inventory.yml
│   ├── setup-ws1.yml
│   ├── setup-inference.yml
│   └── /roles/
├── /configs/
│   ├── /traefik/
│   ├── /bifrost/
│   ├── /dograh/
│   ├── /keycloak/
│   ├── /crowdsec/
│   ├── /opnsense/
│   └── /grafana/
├── /n8n/
│   ├── /workflow-templates/
│   │   ├── /capabilities/       ← cap-*.json (extract after v1 use cases)
│   │   └── /use-case-templates/ ← template-*-main.json
│   ├── /use-cases/              ← deployed use case workflows
│   └── /internal/               ← Hermes/OpenClaw triggered workflows
├── /langfuse/
│   └── /prompts/                ← versioned agent prompts
├── /tests/
│   └── /[usecase]-golden.json   ← QA golden datasets
├── /scripts/
│   ├── new-client.py            ← v2 multi-tenant onboarding
│   ├── backup.py
│   ├── health-check.py
│   └── disaster-recovery.py
└── /docs/
    ├── PROJECT.md               ← this file
    ├── AGENTS.md                ← OpenCode instructions
    └── AIOS_USECASES.md         ← 5 use cases build guide
```

---

## 11. DEV STACK — 7 NON-NEGOTIABLE TOOLS

```
1. OpenCode Desktop    SSH to WS1, builds everything, reads AGENTS.md
2. Git + GitHub        Version control — all configs, workflows, scripts
3. ArgoCD              GitOps CD — push → auto-deploys to Docker stack
4. Ansible             Server setup + disaster recovery (unattended)
5. Hermes Agent        Autonomous 24/7 DevOps — YOU talk via Telegram
6. OpenClaw            Personal AI assistant — WhatsApp/Telegram 24/7
7. GitHub Actions      CI — validates every push before ArgoCD deploys

Dev PC: VS Code + Remote SSH, Bruno, Git, Python 3, OpenCode Desktop
```

---

## 12. PHASES

```
Phase 1 (now — 45 days):
  Both machines set up + all Docker stacks running
  5 use cases built + tested with real users
  Single tenant — one shared platform
  Kubernetes: NO — Docker Compose only

Phase 2 (Month 3-6):
  Multi-tenant (v2) — per-client isolation
  18-40 clients | PKR 197K-582K/mo
  UAE prep: Arabic/English agents
  LLM Wiki implementation
  Add: Postgres replica, Arize Phoenix

Phase 3 (Month 7+):
  60 clients | PKR 940K MRR | Break-even Month 7
  UAE Month 9-12 | US/Canada Month 12-18
  K3s when 100+ clients
  3rd machine for true HA
  Enterprise tier deployments
```

---

*AIOS PROJECT.md — Final Compact Reference*
*Version: v2.0 · May 2026 · Lahore AI Lab*
*15 infrastructure layers | OpenCode + Hermes + OpenClaw | Dograh voice*
*wassim249 LangGraph template | Single tenant v1 | Multi-tenant v2*
