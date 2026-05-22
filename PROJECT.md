# AIOS — AI Operating System
## Complete Project Reference for Claude Code
### Lahore AI Lab · May 2026 · FINAL LOCKED

### Build Status — See CHECKPOINT.md for current progress
```
✅ STEP 1: NVIDIA Quadro M4000 driver installed  (nvidia-driver-470.256.02)
✅ STEP 2: Docker Engine installed               (Docker 29.5.1 + Compose v5.1.3)
✅ STEP 2b: nvidia-container-toolkit configured   (GPU works inside containers)
⬜ STEP 3-14: Remaining layers
```

---

## 1. PROJECT OVERVIEW

### What This Is
AIOS (AI Operating System) is a production-grade, self-hosted hybrid AI platform built in a physical lab in Lahore, Pakistan. Designed to:

1. **Serve as an AI R&D lab** — build, test, prototype AI use cases
2. **Serve as a production template** — same architecture cloned for each SMB client
3. **Power a commercial AI agency** — selling AI Digital Employees to SMBs across Pakistan, UAE, and USA

### Business Context
- **Founder:** Senior IT infrastructure specialist, 20+ years, documented government-scale AI deployment (38,000-school SED)
- **Model:** Sell AI Digital Employees (voice agents, WhatsApp agents, workflow automation) to SMBs
- **Target markets:** Pakistan (Lahore) → UAE (Dubai/Abu Dhabi) → USA/Canada (white-label)
- **Revenue:** PKR 35–75K setup + PKR 12–22K monthly recurring per client
- **Target:** 60 clients by Month 12, PKR 940K MRR

### Core Principle
The lab IS the product. Built and tested here = exactly what clients get. New client = configuration only, zero new infrastructure.

---

## 2. PHYSICAL INFRASTRUCTURE

### Machine 1 — Server (aios)
```
Hostname: aios
OS:       Ubuntu 22.04.5 LTS — bare metal + Docker Engine
IP:       10.0.0.100 (LAN)
Public:   NO — internet via Huawei ONT → Cloudflare tunnel, port 443 only
GPU:      NVIDIA Quadro M4000 — 8GB VRAM, 1664 CUDA cores (Maxwell)
          nvidia-driver-470.256.02 + nvidia-container-toolkit ✅
RAM:      31GB DDR4
Storage:  953.9GB NVMe (850GB free LVM)
Docker:   Docker Engine 29.5.1 + Docker Compose v5.1.3
```

**Server runs 4 layers simultaneously:**

#### Layer A — Docker Compose (FOSS business apps)
`docker-compose-apps.yml` — independent lifecycle
```
Odoo, ERPNext/Frappe, Twenty CRM, SuiteCRM, Calcom, Paperless-ngx,
Docuseal, Planka, Rocket.Chat, Frappe LMS, GnuCash, Metabase
```

#### Layer B — Docker Compose (AI core — AIOS engine)
`docker-compose-aios.yml` — the AIOS engine
```
Traefik, CrowdSec, Keycloak, HashiCorp Vault, Bifrost, Ollama(dev),
LiteLLM(dev), MQTT, Asterisk, FreePBX, n8n+workers, Flowise, Dify,
Paperclip, Hermes, Langfuse, Qdrant, Supabase, Redis, MinIO,
Open WebUI, Grafana, Prometheus, Loki, Portainer, Dashy,
Uptime Kuma, Dozzle, GitOps Agent, Watchtower, Trivy, Frigate, go2rtc
```

#### Layer C — Dev PC (Windows 11 — 10.0.0.13)
```
Role:     Development, Docker Desktop for local prototyping
CPU:      Intel Xeon E-2276G (6C/12T) | RAM: 15.8GB
Docker:   Docker Desktop v29.4.3 — WSL2 backend
Tools:    Claude Code, Git, Python 3, VS Code, Bruno
```

#### Layer D — Lab Intelligence
```
Claude Code Desktop  — AI coding assistant (primary dev tool)
opencode            — AI coding assistant (local fallback)
Hermes Agent        — Autonomous 24/7 server ops (Docker B)
OpenClaw            — Personal assistant via WhatsApp/Telegram
```

### GPU Allocation — Quadro M4000 (8GB VRAM)
```
Model               VRAM     Role
────────────────────────────────────────────
Mistral 7B Q4       ~5GB     Fast lightweight tasks, high throughput
Llama 3 8B Q4       ~5.5GB   General reasoning, HR, inventory
Qwen 2.5 7B Q4      ~5GB     Arabic + Urdu + English multilingual
LLaVA 7B (Ollama)   ~5GB     Visual — reads images, invoices
nomic-embed-text    Minimal  Document embeddings
```
NOTE: 8GB VRAM cannot run 70B+ locally — routes to OpenRouter/Claude API.

### Resource Allocation
```
Layer A (FOSS):      6GB RAM   | 2 vCPU | 200GB NVMe
Layer B (AI core):   21GB RAM  | 6 vCPU | 500GB NVMe + Quadro M4000
OS + overhead:        4GB RAM   | 2 vCPU |  50GB NVMe
Total:               ~31GB     | 10 vCPU | 750GB NVMe (~200GB free)
```

---

## 3. NETWORKING & SECURITY

### 3.1 Physical Network
```
Internet (100Mbps Fiber)
  → Huawei ONT (10.0.0.1 gateway)
    → Server aios (10.0.0.100)
    → Dev PC (10.0.0.13)
```

### 3.2 Security Stack (5 layers — traffic passes all in sequence)
```
Layer 1 — Cloudflare Edge
  DDoS protection, SSL certificates, CDN, DNS

Layer 2 — Huawei ONT (port 443 only via Cloudflare tunnel)
  NAT, minimum surface area

Layer 3 — Traefik (DMZ — 10.10.0.10)
  Reverse proxy, HTTPS termination, container routing, load balancing

Layer 4 — CrowdSec (DMZ — 10.10.0.11)
  WAF, IP reputation, rate limiting, brute force detection

Layer 5 — Keycloak (App zone — 10.20.0.40)
  SSO, multi-tenant isolation, RBAC, OAuth2/OIDC
```

### 3.3 Docker Network Zones (7 isolated)
```
Zone 1 — DMZ:         10.10.0.0/24   Traefik, CrowdSec
                                       Only zone exposed to internet. Port 443 only.
Zone 2 — Application: 10.20.0.0/24   n8n, Flowise, Dify, Open WebUI, Keycloak,
                                       Vault, FreePBX, WireGuard, Paperclip, Hermes
Zone 3 — Data:        10.30.0.0/24   Supabase, Qdrant, Redis, MinIO
                                       internal:true — NO internet access
Zone 4 — AI:          10.40.0.0/24   Bifrost, Ollama(dev), LiteLLM(dev), vLLM
                                       GPU-accelerated via Quadro M4000
Zone 5 — Voice:       10.50.0.0/24   Asterisk, MQTT
Zone 6 — Monitoring:  10.60.0.0/24   Langfuse, Prometheus, Grafana, Loki,
                                       Portainer, Dashy, Uptime Kuma, Dozzle,
                                       GitOps Agent, Watchtower, Trivy, nvidia-smi-exporter
Zone 7 — FOSS:        10.70.0.0/24   ERPNext, Odoo, Twenty CRM, Metabase, Calcom
```

### 3.4 WireGuard VPN
- WireGuard container in app zone (10.20.0.x)
- Admin VPN access for remote management
- No OPNsense needed — Docker zones + CrowdSec + Cloudflare provide equivalent security

### 3.5 Secrets Management — HashiCorp Vault (10.20.0.50)
- ALL API keys, passwords, tokens encrypted at rest
- Injected at container runtime via .env files pulled from Vault
- NEVER hardcode secrets. NEVER commit secrets to Git.

### 3.6 Multi-Tenant Client Isolation
```
Keycloak:   Separate Organization per client
Qdrant:     Separate collection — {client_id}-knowledge
Supabase:   Separate schema per client + RLS enforced
Bifrost:    Separate virtual key + monthly budget limit
n8n:        Separate workflow tagged to client_id
Langfuse:   Separate project per client
Paperclip:  Separate company per client
```

### 3.7 Protocols & Standards
```
Protocol          Standard              Role
────────────────────────────────────────────────────────────
MCP               Anthropic             Standardised tool connections for all agents
A2A               Google                Agent-to-agent communication
OpenTelemetry     CNCF                  Distributed tracing across all services
OAuth2 / OIDC     Industry standard     All auth flows via Keycloak
OpenAI API        De facto LLM standard Bifrost + vLLM both expose this
MQTT              IoT standard          Frigate event bus to n8n
SIP               Telecoms standard     Asterisk trunking
RTSP              Camera standard       All IP cameras to go2rtc
```

---

## 4. DEVELOPMENT LAYER

### 4.1 Architecture Type
AIOS is infrastructure development — Docker Compose configs, n8n workflow JSON, Python scripts, Ansible playbooks, shell scripts. NOT React apps or APIs.

### 4.2 The 7 Non-Negotiable Dev Tools
```
Tool              Role                                    Cannot Replace
────────────────────────────────────────────────────────────────────────────
1. Claude Code    Primary AI dev tool — SSH to server,    Nothing
   Desktop        writes + executes everything.

2. Git + GitHub   Version control for ALL configs,        Nothing
                  workflows, scripts. Full history.
                  Rollback in seconds.

3. GitOps Agent         GitOps CD — watches GitHub 24/7,        Nothing
   (on server)    auto-deploys to Docker stack.

4. Ansible        Server setup + disaster recovery.       Claude Code
                  Idempotent, unattended.                 (needs you present)

5. Hermes Agent   Autonomous 24/7 server ops.             Nothing
   (on server)    Monitors, restarts, alerts.

6. OpenClaw       Personal AI assistant.                  Nothing
   (on laptop)    Inbox, calendar, tasks via WA/Telegram.

7. GitHub Actions CI validation on every push.            Nothing
   Runner         Validates YAML, pytest, Trivy scan.
```

### 4.3 Claude Code Workflow
```
CONNECTS TO: Server via Desktop SSH
READS:       /aios/ (entire project)
             CLAUDE.md (architecture rules automatically)
             PROJECT.md (every decision documented)

WRITES:
  docker-compose-aios.yml / docker-compose-apps.yml changes
  Ansible playbooks, Python scripts (new-client.py, backup.py)
  n8n workflow JSON templates
  GitHub Actions CI, Bifrost configs, Traefik rules

EXECUTES ON SERVER:
  docker-compose up -d
  ansible-playbook setup-server.yml
  python3 new-client.py --client-id clinic-abc
```

### 4.4 Ansible Structure
```
/aios/ansible/
├── inventory.yml              # Server: 10.0.0.100
├── setup-server.yml           # Full server setup — Docker, GPU, dirs
└── /roles/
    ├── docker/                # Install Docker
    ├── nvidia/                # NVIDIA drivers + CUDA
    └── aios-directories/      # /aios/ folder structure
```

### 4.5 Git Branching Strategy
```
main:        production — GitOps Agent deploys from here
dev:         staging — test before promoting
feature/* :  new capabilities, configs

Workflow: feature branch → push → CI validates → PR to dev → test → main → GitOps Agent
```

### 4.6 Directory Structure
```
/aios/
├── CLAUDE.md                        # Claude Code instructions (AUTO-READ)
├── docker-compose-aios.yml          # AI core services (Layer B)
├── docker-compose-apps.yml          # FOSS business apps (Layer A)
├── .env.aios                        # AI core env vars (from Vault)
├── .env.apps                        # Apps env vars (from Vault)
├── /ansible/                        # Server setup playbooks
│   ├── inventory.yml
│   ├── setup-server.yml
│   └── /roles/
├── /configs/
│   ├── /traefik/                    # Traefik routing rules
│   ├── /crowdsec/                   # CrowdSec WAF rules
│   ├── /keycloak/                   # Keycloak realm exports
│   ├── /bifrost/                    # Bifrost routing + budget config
│   └── /grafana/                    # Grafana dashboard JSON
├── /n8n/
│   ├── /workflow-templates/
│   │   ├── /capabilities/           # 20 cap-*.json sub-workflows
│   │   └── /use-case-templates/     # 12 template-*-main.json
│   ├── /clients/                    # Deployed per-client workflows
│   └── /internal/                   # Internal lab workflows
├── /langfuse/
│   └── /prompts/                    # Agent system prompts (versioned)
├── /clients/
│   └── /[client-id]/                # Per-client configs + knowledge docs
├── /scripts/
│   ├── new-client.py                # Client onboarding automation
│   ├── backup.py                    # Nightly backup script
│   ├── health-check.py              # System health verification
│   └── disaster-recovery.py         # Full system restore
└── /docs/
    ├── PROJECT.md                   # Master reference (this file)
    ├── CHECKPOINT.md                # Build progress tracker
    ├── DEPLOYMENT_PLAN.md           # 14-step build plan
    └── /capabilities/               # One .md per capability
```

### 4.7 Environment Variables
```bash
# Server Access
SERVER_HOST=10.0.0.100
SERVER_USER=ai
GATEWAY=10.0.0.1
DEV_PC_IP=10.0.0.13

# Bifrost AI Gateway
BIFROST_URL=http://10.40.0.10:4000
BIFROST_ADMIN_KEY=<from Vault>

# vLLM — local inference (Quadro M4000)
VLLM_URL=http://10.40.0.40:8000
VLLM_API_KEY=<from Vault>

# Cloud LLMs (via Bifrost — do NOT call directly)
ANTHROPIC_API_KEY=<from Vault>
OPENAI_API_KEY=<from Vault>
GOOGLE_API_KEY=<from Vault>
OPENROUTER_API_KEY=<from Vault>

# Voice
DEEPGRAM_API_KEY=<from Vault>
ELEVENLABS_API_KEY=<from Vault>
RETELL_API_KEY=<from Vault>

# WhatsApp
WHATSAPP_TOKEN=<from Vault>
WHATSAPP_PHONE_ID=<from Vault>

# Data (10.30.0.0/24)
SUPABASE_URL=http://10.30.0.10:8000
SUPABASE_KEY=<from Vault>
QDRANT_URL=http://10.30.0.20:6333
REDIS_URL=redis://10.30.0.30:6379
MINIO_URL=http://10.30.0.40:9000

# Monitoring
LANGFUSE_URL=http://10.60.0.10:3000
LANGFUSE_KEY=<from Vault>
```

### 4.8 Critical Development Rules

```
1. NEVER call any LLM API directly — ALL go through Bifrost (http://10.40.0.10:4000)
2. NEVER hardcode secrets — all in Vault, injected at runtime
3. ALWAYS tag n8n workflows with client_id — no cross-client leaks
4. ALWAYS enforce Supabase RLS — schema per client + RLS = double isolation
5. Quadro M4000 has 8GB VRAM — no 70B+ locally, routes to OpenRouter/Claude
6. ALWAYS log every LLM call to Langfuse — this is how we bill clients
7. Data Zone (10.30.0.0/24) has internal:true — NEVER change this
8. ALL new client resources via new-client.py only — never manual
9. ALL capability sub-workflows = zero client hardcoding (variables only)
10. ALWAYS commit to Git before production changes — Git is source of truth
```

### 4.9 Adding New Templates

**New Capability:**
```
1. Prototype in Flowise/Dify → 2. Export to n8n sub-workflow JSON
3. Replace ALL values with variables → 4. Test with 2+ dummy clients
5. Validate in Langfuse → 6. Save to /n8n/workflow-templates/capabilities/
7. Write docs → 8. Update new-client.py → 9. git commit + push
```

**New Use Case (workflow):**
```
1. Build/test in Flowise or Dify → 2. Translate to n8n workflow
3. Test with Ollama dev (zero cost) → 4. Validate with Langfuse
5. Save as template → 6. Document + update new-client.py
```

### 4.10 Dev PC / Laptop Setup (10.0.0.13 — Windows 11)

```
INSTALL:
  VS Code                     code.visualstudio.com
  VS Code Remote SSH plugin   edit files on server from laptop
  Claude Code Desktop         claude.ai/code
  Git                         git-scm.com
  Python 3                    python.org
  Bruno (API testing)         usebruno.com — free, open source

CONNECT TO:
  Server via Claude Code Desktop SSH → primary interface
  Server via VS Code Remote SSH      → backup editor
  All dashboards via browser         → n8n, Grafana, Langfuse, etc.

NOT NEEDED ON LAPTOP:
  Docker daemon (everything runs on server)
  Node.js server, Database, any AIOS service
```

### 4.11 Scripts Reference

```
/aios/scripts/
├── openclaw.py             # AIOS Lab Assistant — CLI for Dev PC (running)
├── hermes.sh               # 24/7 autonomous ops agent (running)
├── new-client.py           # Client onboarding automation (TODO)
├── backup.py               # Nightly encrypted backup (TODO)
├── health-check.py         # On-demand health verification (TODO)
├── disaster-recovery.py    # Full system restore (TODO)
```

---

## 5. SERVICES ARCHITECTURE

All services are Docker containers on the server, split across 7 network zones.

### 5.1 Data Layer (10.30.0.0/24 — internal:true)
```
Service     IP              Role
────────────────────────────────────────────────────
Supabase    10.30.0.10      Operational DB — agent memory, conversations, CRM,
                             user records, per-client schema + RLS
Qdrant      10.30.0.20      Vector DB — one collection per client, RAG knowledge
                             bases, SOPs, FAQs, semantic search
Redis       10.30.0.30      n8n queue (queue mode), session cache, short-term memory
MinIO       10.30.0.40      S3-compatible storage — client docs, recordings, backups
NAS         Future          Add for scale — NFS mount for backups
```

### 5.2 Security Services (App zone + DMZ)
```
Service     IP              Zone         Role
───────────────────────────────────────────────────────────────
Traefik     10.10.0.10     DMZ          Reverse proxy, HTTPS termination
CrowdSec    10.10.0.11     DMZ          WAF, rate limiting, IP reputation
Keycloak    10.20.0.40     App          SSO, multi-tenant, OAuth2/OIDC
Vault       10.20.0.50     App          Secrets management — ALL API keys
```

### 5.3 AI Core (10.40.0.0/24)
```
Service     IP              Role
────────────────────────────────────────────────────
Bifrost     10.40.0.10      AI Gateway — ALL LLM calls, caching, failover,
                             client budgets, prompt injection detection
Ollama      10.40.0.20      DEV inference — LLaVA 7B, nomic-embed-text
LiteLLM     10.40.0.30      DEV gateway — prototyping only
vLLM        10.40.0.40      Production inference — Mistral 7B, Llama 3 8B,
                             Qwen 2.5 7B (GPU-accelerated)
```

### 5.4 Orchestration (10.20.0.0/24)
```
Service        IP              Role
────────────────────────────────────────────────────────────
n8n            10.20.0.10      Master orchestrator — ALL business logic
n8n-worker-1   10.20.0.11      Stateless worker (Redis queue)
n8n-worker-2   10.20.0.12      Stateless worker (Redis queue)
Flowise        10.20.0.20      Visual no-code agent builder
Dify           10.20.0.21      LLM app platform + RAG UI
Open WebUI     10.20.0.30      Chat interface
Paperclip      10.20.0.60      AI company OS — org chart, budgets, heartbeats
Hermes         10.20.0.70      Internal DevOps agent — 24/7 monitoring
FreePBX        10.20.0.80      Call centre GUI — extensions, recordings, CDR
WireGuard      10.20.0.90      Admin VPN for remote access
```

### 5.5 Voice Layer (10.50.0.0/24)
```
Service     IP              Role
────────────────────────────────────────────────────
Asterisk    10.50.0.10      VoIP engine — SIP trunking, call routing, IVR
MQTT        10.50.0.20      Event bus — Frigate events → n8n workflows
```
Voice pipeline: Caller → SIP Trunk → Asterisk → Retell AI/Vapi → Deepgram STT → n8n → Bifrost → vLLM/Claude → ElevenLabs TTS → Asterisk → Caller

### 5.6 Visual AI (App zone)
```
Service     IP              Zone    Role
────────────────────────────────────────────────────────
Frigate     10.20.0.90     App     Real-time object detection (GPU passthrough)
go2rtc      10.20.0.91     App     RTSP stream management
```
Visual pipeline: IP Camera RTSP → go2rtc → Frigate → YOLO → LLaVA description → MQTT → n8n → action

### 5.7 FOSS Business Apps (10.70.0.0/24)
```
App               IP              Role
────────────────────────────────────────────────────────
ERPNext           10.70.0.10      Full ERP — hospital, hotel, manufacturing, HR
Odoo              10.70.0.20      Full ERP — accounting, inventory, CRM
Twenty CRM        10.70.0.30      Open-source Salesforce alternative
Metabase          10.70.0.40      PRIMARY client dashboards — business KPIs
Calcom            10.70.0.50      Appointment scheduling
SuiteCRM          10.70.0.60      Enterprise CRM — campaigns, cases
Paperless-ngx     10.70.0.70      Document management — OCR, archiving
Docuseal          10.70.0.80      E-signing — contracts
Planka            10.70.0.90      Project management (Trello-like)
Rocket.Chat       10.70.0.100     Team communication
Frappe LMS        10.70.0.110     Learning management
GnuCash           10.70.0.120     Lightweight accounting
```

### 5.8 Monitoring & CI/CD (10.60.0.0/24)
```
Service           IP              Role
────────────────────────────────────────────────────────────
Langfuse          10.60.0.10      LLM observability + prompt registry
Prometheus        10.60.0.20      Metrics — CPU, RAM, GPU, disk
Grafana           10.60.0.30      Visualisation — infra + LLM + business
Loki              10.60.0.40      Log aggregation — all containers
Portainer         10.60.0.50      Docker container management UI
Uptime Kuma       10.60.0.60      Service uptime → WhatsApp alerts
Dashy             10.60.0.70      Central navigation homepage
Dozzle            10.60.0.80      Real-time Docker log viewer
nvidia-smi-exp    10.60.0.90      GPU metrics exporter
GitOps Agent            10.60.0.100     GitOps CD — auto-deploy from GitHub
Watchtower        10.60.0.110     Auto-update containers
Trivy             10.60.0.120     Container security scanning
```

### 5.9 Input Channels (Tier 1)
```
Channel              Tool / Protocol              What It Carries
─────────────────────────────────────────────────────────────────
Voice calls          Asterisk SIP + Retell AI     Audio calls
WhatsApp             Meta WhatsApp Business API   Text, images, voice notes, docs
Web chat             React widget + n8n webhook   Text conversations
REST API/Webhooks    n8n webhook nodes            External triggers, form submissions
IP Cameras           RTSP → go2rtc → Frigate      Live video feeds
Document upload      Supabase Storage + n8n       PDFs, invoices, contracts, images
Email inbound        IMAP/SMTP via n8n            Email triggers, attachments
SMS                  Twilio                       Alerts, reminders, OTPs
```

### 5.10 External Integrations (via n8n + Bifrost + MCP)
```
Integration           Protocol        Use Case
──────────────────────────────────────────────────────────────────
WhatsApp Business API Meta webhook    All WhatsApp agents
Twilio                REST API        SMS, voice backup, OTPs
Google Calendar       OAuth → n8n     Appointment booking
Microsoft 365         OAuth → n8n     Enterprise integrations
JazzCash / EasyPaisa  REST API        Pakistan payments
Stripe                REST API        UAE / US payments
MCP servers           Anthropic MCP   Standardised tool connections
Retell AI / Vapi      REST API        Voice agent platform
Deepgram Nova 3       WebSocket       STT — Arabic/Urdu/English
ElevenLabs            REST API        TTS — 29+ languages
```

### 5.11 Dashboards
```
SysOps (YOUR team):    Dashy, Grafana, Langfuse, Portainer, CrowdSec,
                       Keycloak admin, Bifrost dashboard, n8n dashboard,
                       Paperclip admin, Hermes dashboard (port 9119)
Client-facing:         Metabase (primary), React + Supabase white-label portal,
                       n8n reporting agents (auto WhatsApp/email reports),
                       Grafana client org (tech-savvy clients)
```

---

## 6. AI LAYER & LLM ROUTING

### 6.1 Production AI Gateway — Bifrost (10.40.0.10:4000)
ALL LLM calls go through Bifrost. NEVER call APIs directly. Bifrost provides:
- 11μs overhead, 5000+ RPS
- Semantic caching (40-60% cost saving)
- Per-client virtual keys + monthly budget controls
- Automatic failover (local → OpenRouter → Claude)
- Prompt injection detection + PII sanitisation
- MCP support, OpenAI-compatible endpoint
- Full cost tracking per client per call

### 6.2 All Models — Complete Reference
```
Model               Location         VRAM/Cost     Capabilities
──────────────────────────────────────────────────────────────────────────
Mistral 7B Q4       vLLM (local)     ~5GB free     FAQ, classification, routing
Llama 3 8B Q4       vLLM (local)     ~5.5GB free   General reasoning, HR, inventory
Qwen 2.5 7B Q4      vLLM (local)     ~5GB free     Arabic/Urdu conversation
LLaVA 7B            Ollama (local)   ~5GB free     Image/invoice reading
nomic-embed-text    Ollama (local)   Minimal free  Document embeddings → Qdrant
Claude 4 Sonnet     Anthropic (API)  Per-token     Complex docs, legal, long context (PRIMARY)
GPT-4o              OpenAI (API)     Per-token     Vision, structured extraction
Gemma 4             OpenRouter (API) Per-token     General reasoning, code, multilingual
Gemini 2.0          Google (API)     Per-token     Multimodal, very long context
Any 70B+/other      OpenRouter (API) Per-token     DeepSeek, Qwen 72B, 200+ models
```

### 6.3 Bifrost Routing Logic
```
Task Type                           Routes To                                    Reason
─────────────────────────────────────────────────────────────────────────────────────────
Simple FAQ, routing, classification  Mistral 7B (local vLLM)                     Fast, free
Arabic/Urdu conversation             Qwen 2.5 7B (local vLLM)                    Best multilingual
General reasoning, HR, inventory     Llama 3 8B (local vLLM)                     High quality, zero cost
General reasoning (API supplement)   Gemma 4 via OpenRouter (API)                Strong + cheaper than Claude
Code, structured output              Gemma 4 / Claude 4 Sonnet via OpenRouter    Both excellent at code
Complex docs, legal, long context    Claude 4 Sonnet (API)                       Frontier quality needed
Invoice/image reading                GPT-4o (API) + LLaVA (local)               Best vision models
Any hosted model needed              OpenRouter (API)                            200+ models — Llama, Mistral,
                                                                                  Qwen, DeepSeek, Gemma, etc.
Local models under load/down         OpenRouter → Claude (auto-failover)          Multi-tier auto-fallback
Cached/repeated queries              Bifrost semantic cache                      No LLM call at all
70B+ reasoning                       OpenRouter / Claude API (cloud)             Cannot fit in 8GB VRAM
```

### 6.4 Routing Priority (every LLM call)
```
1. Bifrost semantic cache hit  → return cached response (zero cost)
2. Local vLLM (Mistral/Llama/Qwen) → run on Quadro (zero cost)
3. OpenRouter API → pay-per-token for hosted models
4. Claude API → direct Anthropic for frontier tasks
Failover: if local models down → skip to OpenRouter → if OpenRouter fails → Claude
```

### 6.5 Prompt Registry + RAG Pipeline
```
Tool              Where           Role
──────────────────────────────────────────────────────────────────
Langfuse          Mon zone        ALL system prompts stored, versioned, managed
                                   centrally. Agents pull at runtime.
nomic-embed-text  AI zone         Embedding model — docs → vectors
LlamaIndex        App zone        Document chunking + RAG pipeline
```

### 6.6 Hybrid Cloud Architecture
```
ON-PREM (never leaves):
  Client data, agent memory, conversations, documents
  RAG knowledge bases, business logic, workflow execution
  Camera feeds, voice recordings, all FOSS app data

CLOUD (necessary only — via Bifrost):
  LLM inference (text only — Bifrost strips PII)
  STT audio (Deepgram — voice call audio)
  Encrypted backups (S3 — AES-256 encrypted)
  Email (SES — reports/notifications)
  Static assets (CloudFront — dashboard CSS/JS)

AWS HYBRID ($200 free tier):
  S3 backups, CloudFront CDN, SES email, EC2 overflow, Lambda webhooks
```

---

## 7. CAPABILITIES LAYER

Capabilities sit between Core Infrastructure and Use Cases. Each capability = combination of multiple tiers. Built once. Reused across all industries.

```
#   Capability                    Tiers Used                          Industries
────────────────────────────────────────────────────────────────────────────────
1   Voice Conversation AI         T1+T3+T5+T6+T7                      Clinic, Hotel, Call centre
2   WhatsApp Conversational AI    T1+T3+T6+T7                         All industries
3   Appointment Booking           T1+T3+T6+T7+T8(Calcom)              Clinic, Salon, Legal
4   Lead Qualification            T1+T3+T6+T7+T8(CRM)                 Real estate, Insurance
5   FAQ + Customer Support        T1+T3+T6+T7(Qdrant RAG)             Any customer-facing
6   Document Processing           T1+T3(LLaVA)+T6+T7                  Legal, Accounting, HR
7   Order & Inventory Management  T1+T3+T6+T7+T8(ERPNext)             Pharmacy, Retail
8   HR Self-Service               T1+T3+T6+T7+T8(ERPNext HR)          Any 10+ employee company
9   Automated Reporting           T3+T6(n8n cron)+T7+T9(Metabase)     All industries
10  Visual Intelligence           T1(cameras)+T4+T3(LLaVA)+T6         Retail, Security, School
11  Proactive Notifications       T6(n8n)+T1(WhatsApp/SMS)+T7         All industries
12  System Integration            T6(n8n)+T8+MCP                      Any business with legacy IT
13  Multilingual AI               T3(Qwen 7B)+T5(Deepgram)            All UAE/Pakistan industries
14  Payment Processing            T6(n8n)+T8(JazzCash/Stripe)         Retail, Clinic, Academy
15  Email Automation              T1(IMAP)+T3+T6(n8n)                 Legal, Accounting, RE
16  Predictive Analytics          T7(data)+T9(metabase+sklearn)       Retail, Pharmacy, Mfg
17  Attendance & Access Control   T4(Frigate face)+T8(ERPNext HR)     School, Factory, Office
18  Contract & E-Signing          T3+T6(n8n)+T8(Docuseal+Paperless)   Legal, Real estate, HR
19  Multi-Channel Routing         T1+T6(n8n routing)+T5               Call centre, Support
20  Agent Escalation              T6(n8n human-in-loop)+T1(WhatsApp)  All industries
```

---

## 8. USE CASES

Each use case = 1 n8n workflow + 1 Qdrant collection + 1 Keycloak tenant + 1 Bifrost virtual key + 1 Langfuse prompt + 1 Paperclip company agent. Onboarding = 2-3 hours.

```
#   Use Case                  Channel              LLM                  Replaces              App
─────────────────────────────────────────────────────────────────────────────────────────────────────
1   Clinic AI Receptionist    Voice + WhatsApp     Llama 3 8B + Qwen    Manual receptionist   ERPNext Hospital
2   HR AI Assistant           WhatsApp + Web       Mistral 7B           HR admin routine      ERPNext HR
3   Real Estate Lead Agent    WhatsApp + Voice     Claude 4 Sonnet      Manual follow-up      Twenty CRM + Calcom
4   Retail Inventory AI       Web + WhatsApp       Mistral 7B + Frigate  Manual stock mgmt     ERPNext POS
5   Accounting AI             WhatsApp + Web       GPT-4o + LLaVA       Manual data entry     Paperless-ngx + GnuCash
6   Pharmacy AI               WhatsApp + Voice     Llama 3 8B + Frigate  Manual ordering       ERPNext POS
7   Hotel Concierge AI        Voice + WhatsApp     Claude 4 + ElevenLabs Front desk routine   ERPNext Hotel
8   Call Centre AI            Voice (Asterisk)     Qwen 7B Urdu/Arabic  Human agents          FreePBX + Asterisk
9   Legal AI                  Web + Email          Claude 4 long ctx    Manual doc review     Paperless-ngx + Docuseal
10  Academy AI                WhatsApp + Web       Mistral + Qwen       Admin staff           Frappe LMS + ERPNext Edu
11  Security AI               Camera feeds         Frigate + LLaVA      Manual monitoring     Frigate pipeline
12  Logistics AI              WhatsApp + API       Mistral 7B           Manual tracking       ERPNext + n8n
```

---

## 9. DATA FLOWS

### WhatsApp Agent — Complete Request Lifecycle
```
Client sends WhatsApp message
→ Meta webhook → Cloudflare → Huawei ONT → Traefik → CrowdSec
→ Keycloak auth (tenant validated)
→ n8n workflow (client-specific, tagged to tenant)
→ Bifrost guardrails (prompt injection scan)
→ Qdrant semantic search (client knowledge base RAG)
→ Langfuse (pulls versioned system prompt for this client)
→ Bifrost semantic cache check (cached? return immediately)
→ Bifrost routes to vLLM (local) OR OpenRouter/Claude API (cloud)
→ Langfuse logs: prompt + response + cost + latency + tokens + model
→ OpenTelemetry traces full request path
→ n8n formats reply → WhatsApp API → client receives answer
Total: under 3 seconds end-to-end
```

### Voice Call — Complete Lifecycle
```
Caller dials → SIP trunk → Asterisk (Docker Voice)
→ Retell AI / Vapi (conversation orchestration)
→ Deepgram Nova 3 STT (Arabic/Urdu/English real-time)
→ n8n webhook → same pipeline as WhatsApp above
→ Bifrost → vLLM / Claude → response text
→ ElevenLabs TTS (natural voice synthesis)
→ Audio back → Asterisk → caller
Call recorded. Full transcript logged in Langfuse.
```

### Visual AI — Camera Event Pipeline
```
IP camera RTSP → go2rtc → Frigate NVR
→ YOLO on Quadro M4000 (detects object: person/vehicle/face)
→ LLaVA describes: "delivery driver at front door"
→ MQTT event → n8n workflow fires
→ n8n → Bifrost → LLM → decides action
→ WhatsApp alert to owner + Supabase log + Grafana update
```

### Knowledge Document Ingestion
```
Admin uploads .md / PDF / SOP → Supabase Storage
→ n8n ingestion workflow → LlamaIndex chunks document
→ nomic-embed-text generates vectors → Qdrant stores in client's collection
Agent immediately has access to new knowledge. Zero restart.
```

### Nightly Backup Pipeline
```
Cron 2:00 AM → n8n workflow
→ pg_dump Supabase → compress → encrypt → S3
→ Qdrant snapshot → compress → server local + S3
→ n8n export → server local + S3 → MinIO sync → S3
→ WhatsApp success notification
```

---

## 10. CLIENT DEPLOYMENT GUIDE

### What Goes vs What Stays
```
REMOVED for client (lab-only):
  Claude Code, Hermes Agent, OpenClaw, Paperclip internal company,
  LiteLLM, Ollama dev, GitOps Agent, Flowise/Dify (optional)

KEPT for client:
  All Tiers 1-10, relevant FOSS apps, Paperclip client company,
  Metabase dashboards, Grafana client org, all monitoring
```

### Client Onboarding Steps
```
Step  Action                                   Tool              Time
─────────────────────────────────────────────────────────────────────────
1     Create Keycloak tenant                   Keycloak admin    5 min
2     Create Qdrant collection                 Qdrant API        2 min
3     Create Supabase schema + RLS             Supabase dash     5 min
4     Create Bifrost virtual key + budget      Bifrost admin     2 min
5     Create Paperclip company                 Paperclip dash    5 min
6     Upload knowledge docs → Qdrant           n8n ingestion     30 min
7     Configure system prompt in Langfuse      Langfuse UI       20 min
8     Clone n8n main workflow from template    n8n dashboard     30 min
9     Connect WhatsApp or voice number         WA API + Retell   15 min
10    Test end-to-end → demo → sign-off        Manual            30 min
─────────────────────────────────────────────────────────────────────────
      TOTAL                                                     2-3 hours
```

---

## 11. PHASES & SCALE PLAN

### Phase 1 — Lab (Now, 45 days)
```
Infrastructure:  1 server Docker Engine + 1 Dev PC
Docker:          Layer A + Layer B deployed
Goal:            5 working prototypes — clinic, HR, real estate, retail, accounting
Team:            Senior AI Engineer + Voice Dev + Full-Stack Dev + QA/DevOps
Kubernetes:      NO — Docker Compose only
```

### Phase 2 — First Clients (Month 3-6)
```
Clients:         3 → 18
Revenue:         PKR 197K → PKR 582K/month
Stack:           Same Docker Compose — add n8n workers as needed
UAE prep:        Bilingual Arabic/English agents
```

### Phase 3 — Scale (Month 7+)
```
Break-even:      Month 7 (25 clients, PKR 742K)
Month 12 target: 60 clients, PKR 940K MRR
UAE entry:       Month 9-12 (government mandate = forced demand)
US/Canada:       Month 12-18 (white-label partnerships)
Kubernetes:      Only if scaling beyond 1 server
HA:              Add 2nd physical server for true failover
```

### What We Don't Have Yet
```
Feature               Status        When
──────────────────────────────────────────────────────
True HA               Not yet       Phase 3 — 2nd machine
Large model 70B+      Cloud only    8GB VRAM limit
Multi-region          Not yet       Phase 3 — UAE DC
Postgres replica      Partial       Phase 2
Full SOC2             Partial       Phase 2 — audit logs exist
Dedicated NAS         Not yet       Phase 2
```

---

## 12. MARKET CONTEXT

### Target Markets
```
Phase       Market              Timing        Strategy
──────────────────────────────────────────────────────────────
Phase 1     Pakistan (Lahore)   Now           Direct sales — clinics, HR, real estate,
                                               pharmacies, academies
                                               PKR 35-75K setup + PKR 12-22K MRR
Phase 2A    UAE (Dubai/Abu Dhabi) Month 9-12  Gov mandate = forced demand
                                               3-4x Pakistan pricing. $1,500 + $450/mo
Phase 2B    US & Canada         Month 12-18   White-label with local agencies
```

### 2026 Market Reality
```
- 64% enterprises using AI (NVIDIA 2026)
- 57% SMBs investing in AI — up from 36% in 2023
- 7% SMBs running production AI agents vs 34% enterprises
- 93/100 SMBs have NO AI agents — this IS the market
- $52.62B AI agent market by 2030 at 46.3% CAGR
- UAE: 50% federal services mandated to agentic AI (April 23, 2026)
```

---

## 13. QUICK REFERENCE

### Service Ports
```
Bifrost:    http://10.40.0.10:4000   vLLM:       http://10.40.0.40:8000
n8n:        http://10.20.0.10:5678   Qdrant:     http://10.30.0.20:6333
Supabase:   http://10.30.0.10:8000   Redis:      redis://10.30.0.30:6379
MinIO:      http://10.30.0.40:9000   Langfuse:   http://10.60.0.10:3000
Grafana:    http://10.60.0.30:3000   Portainer:  http://10.60.0.50:9000
Dashy:      http://10.60.0.70:80     Prometheus: http://10.60.0.20:9090
Keycloak:   http://10.20.0.40:8080   Vault:      http://10.20.0.50:8200
Traefik:    http://10.10.0.10:80/443 Asterisk:   SIP 10.50.0.10
MQTT:       http://10.50.0.20:1883   Ollama:     http://10.40.0.20:11434
```

### By Machine
```
Server Docker Layer A:   Odoo, ERPNext, Twenty CRM, SuiteCRM, Calcom,
                          Paperless-ngx, Docuseal, Planka, Rocket.Chat,
                          Frappe LMS, GnuCash, Metabase
Server Docker Layer B:   Traefik, CrowdSec, Keycloak, Vault, Bifrost,
                          LiteLLM(dev), Ollama(dev), MQTT, Asterisk, FreePBX,
                          n8n+workers, Flowise, Dify, Paperclip, Hermes,
                          Langfuse, Qdrant, Supabase, Redis, MinIO,
                          Open WebUI, Grafana, Prometheus, Loki, Portainer,
                          Dashy, Uptime Kuma, Dozzle, GitOps Agent, Watchtower,
                          Trivy, GitHub Actions Runner
Server GPU:              vLLM, Frigate, LLaVA, YOLO, go2rtc,
                          nvidia-smi exporter, Ollama (GPU models)
Dev PC:                  Claude Code, OpenClaw, Docker Desktop, WSL2
Cloud APIs:              Claude 4 Sonnet, GPT-4o, Gemma 4, Gemini,
                          OpenRouter (200+), Deepgram, ElevenLabs,
                          Retell AI, WhatsApp API, Twilio
AWS:                     S3, CloudFront, SES, EC2 t2.micro, Lambda
```

### Model Routing Quick Reference
```
Task                          Model                          Reason
────────────────────────────────────────────────────────────────────────
Simple FAQ, classification    Mistral 7B (vLLM)              Fast + free
Arabic/Urdu conversation      Qwen 2.5 7B (vLLM)            Best multilingual
General reasoning, HR tasks   Llama 3 8B (vLLM)             Free, quality
General reasoning (API)       Gemma 4 (OpenRouter)          Strong + cheap
Complex docs, legal, long ctx Claude 4 Sonnet (API)          Frontier
Code, structured output       Gemma 4 / Claude 4 (API)      Both excellent
Invoice/image reading         GPT-4o + LLaVA                Best vision
Any other model               OpenRouter (API)              200+ models
Cache hits                    Bifrost cache                 Zero cost
Local down                    OpenRouter → Claude (failover) Auto-fallback
70B+ reasoning                OpenRouter / Claude (API)     8GB VRAM limit
```

---

## 14. CAPABILITIES — TECHNICAL IMPLEMENTATION

### 14.1 What a Capability Is
A capability is a **reusable n8n sub-workflow template** with variable inputs and no client hardcoding. It does ONE job. It knows nothing about which client is calling it.

**Capability IS:** n8n sub-workflow JSON in `/workflow-templates/capabilities/`, called by "Execute Sub-Workflow" node, reused across unlimited clients.
**Capability IS NOT:** A Docker container, separate service, or architecture tier.

### 14.2 Three Core Concepts
```
CAPABILITY  = Reusable sub-workflow (the building block)
              Does ONE job. Variables only. No client context.
              Example: cap-appointment-booking.json

MAIN WORKFLOW = Client-specific orchestrator (the manager)
              Receives input. Routes. Chains capabilities.
              Client variables filled at clone time.
              Example: clinic-abc-main.json

AGENT       = The AI entity with personality, memory, and goal
              Paperclip entry + Langfuse prompt + n8n workflow
              Example: "Sarah — Clinic ABC Receptionist"
```

### 14.3 n8n Folder Structure
```
n8n/
├── /workflow-templates/
│   ├── /capabilities/                  ← 20 sub-workflows
│   │   ├── cap-voice-conversation.json
│   │   ├── cap-whatsapp-conversational.json
│   │   ├── cap-appointment-booking.json
│   │   ├── cap-lead-qualification.json
│   │   ├── cap-faq-support.json
│   │   ├── cap-document-processing.json
│   │   ├── cap-inventory-management.json
│   │   ├── cap-hr-selfservice.json
│   │   ├── cap-automated-reporting.json
│   │   ├── cap-visual-intelligence.json
│   │   ├── cap-proactive-notifications.json
│   │   ├── cap-system-integration.json
│   │   ├── cap-multilingual.json
│   │   ├── cap-payment-processing.json
│   │   ├── cap-email-automation.json
│   │   ├── cap-predictive-analytics.json
│   │   ├── cap-attendance-access.json
│   │   ├── cap-contract-esigning.json
│   │   ├── cap-multichannel-routing.json
│   │   └── cap-agent-escalation.json
│   │
│   └── /use-case-templates/            ← 12 main workflows
│       ├── template-clinic-main.json
│       ├── template-hr-main.json
│       ├── template-realestate-main.json
│       ├── template-retail-main.json
│       ├── template-accounting-main.json
│       ├── template-pharmacy-main.json
│       ├── template-hotel-main.json
│       ├── template-callcentre-main.json
│       ├── template-legal-main.json
│       ├── template-academy-main.json
│       ├── template-security-main.json
│       └── template-logistics-main.json
│
└── /clients/                           ← deployed per client
    └── /[client-id]/
        └── [client-id]-main.json       ← cloned from template
```

### 14.4 Capability Internal Structure
```
INPUT:  variables passed from main workflow
        { client_id, collection_id, prompt_key, model, [capability-specific vars] }

NODES:  logic steps using Tier 3-8 tools (Bifrost, Qdrant, Supabase, ERPNext, etc.)

OUTPUT: { success: true/false, [capability-specific result data] }
```
KEY RULE: No client name, no client data hardcoded. Everything = variable.

### 14.5 Main Workflow Internal Structure
```
[NODE 1] Trigger — Webhook (WhatsApp) / SIP (Voice) / Cron
[NODE 2] Set Variables — client_id, collection_id, prompt_key, model, erp_url
[NODE 3-N] Execute Sub-Workflow (chained capabilities)
[FINAL] Log — Supabase conversation + Langfuse cost/tokens
```

### 14.6 Chaining Example — Clinic Booking
```
Patient: "Dr Ahmed se appointment chahiye kal 3 baje" (Urdu)

[MAIN] → [cap-multilingual] → detects Urdu, translates
       → [cap-intent-detection] → intent: appointment, entities: Dr Ahmed, tomorrow, 3pm
       → [IF/SWITCH] → appointment_booking
       → [cap-appointment-booking] → check ERPNext availability
                                    → query Qdrant rules
                                    → Bifrost → Qwen 2.5 7B
                                    → book in ERPNext + Google Calendar
       → [cap-proactive-notifications] → WhatsApp confirmation in Urdu
       → [Supabase log + Langfuse log]
```

### 14.7 Time Estimates
```
Add capability to existing client:    30-60 min
Onboard NEW client (automated):       10-12 min (new-client.py)
  + Manual (prompt + docs + test):    45-50 min
  = Total to live:                    ~1 hour
```

---

## 15. NEW CLIENT ONBOARDING — FORM FIELDS

### Required Inputs for new-client.py
```
BASIC INFO
  client_id, client_name, industry, contact_name, contact_phone, contact_email

LANGUAGE & REGION
  primary_language (urdu/arabic/english), secondary_language, region, timezone

AI CONFIGURATION
  preferred_model (qwen-2.5-7b), monthly_budget (USD), agent_name, agent_personality

CAPABILITIES (true/false — 18 toggles)
  voice_conversation, whatsapp_conversational, appointment_booking, faq_support,
  lead_qualification, document_processing, inventory_management, hr_selfservice,
  proactive_notifications, visual_intelligence, payment_processing, email_automation,
  predictive_analytics, attendance_access, contract_esigning, multichannel_routing,
  agent_escalation, multilingual (auto if language != english)

CHANNELS
  whatsapp_number, voice_number, web_chat, email_inbound

INTEGRATIONS
  erp_type, erp_url, erp_api_key, calendar_type, calendar_id, crm_type, payment_gateway

AWS RESOURCES
  create_s3_backup, create_cloudfront, create_ses_domain
```

### What new-client.py Automates
```
  ✅ Keycloak tenant           ✅ Qdrant collection ({client_id}-knowledge)
  ✅ Supabase schema + RLS     ✅ Bifrost virtual key + budget
  ✅ Paperclip company + agent ✅ Langfuse project
  ✅ n8n main workflow cloned  ✅ All variables filled
  ✅ Capabilities enabled      ✅ SIP extension (Asterisk)
  ✅ WhatsApp webhook          ✅ AWS S3 + CloudFront (if selected)
```

### What Requires Manual Input (cannot automate)
```
  ❌ System prompt content in Langfuse (15-20 min)
  ❌ Knowledge base docs → Qdrant (20-30 min)
  ❌ End-to-end test (15 min)
```

### Script Output Example
```
┌─────────────────────────────────────────────────┐
│ AIOS NEW CLIENT ONBOARDED                       │
│ Client ID:    clinic-abc        Industry: Clinic│
│ Agent Name:   Sarah             Language: Urdu  │
│ ─────────────────────────────────────────────── │
│ Keycloak: ✅  Qdrant: ✅  Supabase: ✅          │
│ Bifrost: ✅   Paperclip: ✅  n8n: ✅            │
│ WhatsApp: ✅  SIP: ✅       AWS S3: ✅          │
│ ─────────────────────────────────────────────── │
│ MANUAL (45 min): Fill prompt → Upload docs      │
│                  → Test WhatsApp → Test Voice   │
│ Automation: 11 min  │  Manual: ~45 min          │
│ Total to live: ~1 hour                          │
└─────────────────────────────────────────────────┘
```

---

## 16. PHASE 1 DELIVERABLES

### Week-by-Week Build Plan

```
WEEK 1: Infrastructure setup
  Server configured — Docker, GPU, networks
  Docker Layer A (FOSS) + Layer B (AI core) deployed
  All services accessible via Dashy

WEEK 2: Capability templates — batch 1
  cap-voice-conversation, cap-whatsapp-conversational,
  cap-appointment-booking, cap-multilingual,
  cap-intent-detection, cap-faq-support

WEEK 3: Capability templates — batch 2
  cap-lead-qualification, cap-document-processing,
  cap-inventory-management, cap-hr-selfservice,
  cap-proactive-notifications, cap-agent-escalation

WEEK 4: Remaining capabilities + first use cases
  All remaining 8 capabilities
  template-clinic-main.json, template-hr-main.json

WEEK 5-6: Remaining use cases + first client
  All 10 remaining use case templates
  new-client.py script built + tested
  First real client deployed end-to-end
```

### Definition of Done — Capability
```
✅ Sub-workflow in n8n with all variable inputs
✅ All external calls through Bifrost
✅ All data queries through Qdrant (collection_id variable)
✅ Prompts pulled from Langfuse (prompt_key variable)
✅ Success + failure outputs defined
✅ Langfuse logging added
✅ Tested with 2+ client variable sets
✅ Documented in /docs/capabilities/[name].md
```

### Definition of Done — Use Case Template
```
✅ Main workflow in n8n with all client variables
✅ Correct capabilities chained in correct order
✅ Intent routing logic complete (IF/SWITCH)
✅ Logging to Supabase + Langfuse
✅ Tested with dummy client data
✅ new-client.py supports this industry
```

---

*AIOS PROJECT.md — Complete Reference*
*Version: 4.0 · May 2026 · Lahore AI Lab*
*Infra: 1 Server (Quadro M4000 8GB) · 31GB RAM · 953GB NVMe · TP-Link NAT → Cloudflare*
*~40 Docker containers · 7 network zones · Bifrost AI Gateway · n8n orchestration*
*All decisions locked. Do not modify architecture without updating this document.*
