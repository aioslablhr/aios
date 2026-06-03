# AIOS — AI Operating System
## 2026 Reference Architecture — Single-Server Production Stack
### Lahore AI Lab · June 2026 · ARCHITECTURE LOCKED

---

## 1. ARCHITECTURE DECISION — LOCKED

### Physical Lab — LOCKED
```
1 Workstation Server (10.0.0.100) — all infrastructure runs here
  ├── 2 IP cameras → Frigate + YOLO (local GPU, primary)
  ├── 1 Cisco 7962G (Ext 9000) — SIP phone
  ├── N softphones (MicroSIP/Zoiper) — Ext 100-104+
  └── All Docker containers, all AI services
```

**No second machine. No KVM. No OPNsense. No Issabel VM.** Docker zones + CrowdSec + Cloudflare provide equivalent security. Single-server architecture is the locked decision.

### External Services — FALLBACKS ONLY (wired in, optional)
| Service | Role | When Used |
|---|---|---|
| **OpenRouter** | Cloud LLM inference | When local GPU busy or task beyond Qalb |
| **ElevenLabs** | Urdu TTS cloud boost | When XTTS-v2-Urdu-FT quality insufficient |
| **Deepgram** | Urdu STT cloud boost | When Whisper accuracy insufficient |
| **Twilio** | SMS alerts | Outbound SMS channel |
| **Meta WhatsApp API** | WhatsApp messaging | Primary messaging channel |
| **Cloudflare** | DNS, SSL, DDoS | Always — edge security |

### Why This Architecture
- Single server = zero network complexity, maximum reliability
- All local inference = zero per-call cost for primary services
- Cloud fallbacks = quality boost when needed, not required for operation
- Docker network zones = same security as physical VMs without the overhead
- SMB market doesn't need HA — they need affordable, working AI today

---

## 2. PROJECT OVERVIEW — TWO LAYERS

### Layer 1: AI Infrastructure (the engine room)
AIOS is a **2026-aligned best-practice self-hosted AI stack** — production-grade, scalable, state-of-the-art:
- 7-layer Docker architecture: Security → Data → Inference → Orchestration → Voice
- 8 isolated network zones (DMZ, App, Data, AI, Voice, Mon, FOSS, Dev)
- Bifrost AI Gateway | Langfuse observability | Qdrant vector store
- Asterisk → Dograh → Whisper → Bifrost → TTS (local primary, cloud fallback)
- CrowdSec WAF + Traefik + Cloudflare (defense in depth)
- All infrastructure runs on a single server (NVIDIA Quadro M4000)

### Layer 2: AI Transformation (the product)
Running ON the infrastructure — **4 AI Digital Employees replacing manual business processes**:
- Smart Surveillance (Frigate → GPU vision → n8n alerts)
- Smart HR & Payroll (face recognition + GPS → attendance + salary)
- Smart Sales CRM (WhatsApp leads → pipeline → closing)
- AI Voice Receptionist (SIP calls → AI conversation → booking)

### Business Context
- **Founder:** Senior IT infrastructure specialist, 20+ years, documented government-scale AI deployment (38,000-school SED)
- **Model:** Sell AI Digital Employees (AI Transformation Layer) to SMBs, running on the AIOS Infrastructure Layer
- **Target markets:** Pakistan (Lahore) → UAE (Dubai/Abu Dhabi) → USA/Canada (white-label)
- **Revenue:** PKR 35–75K setup + PKR 12–22K monthly recurring per use case per client
- **Target:** 60 clients by Month 12, PKR 940K MRR

### Core Principle
The AIOS Infrastructure Layer is the reference architecture. The AI Transformation Layer (use cases) is the product. Build and test the infrastructure once — deploy AI Digital Employees on top.

---

## 2. PHYSICAL INFRASTRUCTURE — LOCKED

### Machine 1 — Server (aios) — THE ONLY MACHINE
```
Hostname:   aios
OS:         Ubuntu 22.04.5 LTS — bare metal + Docker Engine
IP:         10.0.0.100 (LAN)
Public:     NO — internet via TP-Link NAT → Cloudflare tunnel, port 443 only
GPU:        NVIDIA Quadro M4000 — 8GB VRAM, 1664 CUDA cores (Maxwell)
            nvidia-driver-470.256.02 + nvidia-container-toolkit ✅
RAM:        31GB DDR4
Storage:    953.9GB NVMe (LVM extended 100→500GB)
Docker:     Docker Engine 29.5.1 + Docker Compose v5.1.3
```

### Machine 2 — Dev PC (10.0.0.13 — Windows 11)
```
Role:       Development only — VS Code, Claude Code, Git, Python 3, Bruno
CPU:        Intel Xeon E-2276G (6C/12T) | RAM: 15.8GB
Docker:     Docker Desktop v29.4.3 — WSL2 backend (local prototyping only)
NOT a server. NO production services run here.
```

**No second server. No KVM VMs. No OPNsense. No Issabel. This is locked.**

### GPU VRAM Budget — Quadro M4000 (8GB) — LOCKED
```
Model                          VRAM    Type             Priority
────────────────────────────────────────────────────────────────────────
nomic-embed-text               ~0.3GB  Embeddings       ALWAYS loaded
Qalb-1.0-8B-Instruct (Q4)      ~5.5GB  Urdu LLM         PRIMARY — always loaded
XTTS-v2-Urdu-FT                ~2GB    Urdu TTS          On-demand, swaps with Chatterbox
LLaVA 7B (Q4)                  ~4.5GB  Vision            On-demand, swaps with Qalb
Chatterbox TTS (GPU)           ~1.5GB  English TTS       On-demand, swaps with XTTS
Whisper STT                    ~1GB    Transcription     CPU fallback always available
Kokoro TTS                     0 (CPU) English TTS       CPU — always available
Frigate YOLO                   ~1-2GB  Object detection  Dedicated GPU share
```

**VRAM strategy:** Qalb + nomic-embed-text fit permanently (~5.8GB). Other models load/unload on demand via Ollama. Ollama manages model swapping automatically.

### AIOS Infrastructure Layer — 7 Architectural Layers

#### Layer 0 — Networking & Security
```
Cloudflare → TP-Link NAT → Traefik → CrowdSec → Keycloak → Vault
7 Docker zones (DMZ, App, Data, AI, Voice, Mon, FOSS)
No OPNsense needed — Docker zones + CrowdSec + Cloudflare = equivalent security
```

#### Layer 1 — Data
```
PostgreSQL (pgvector), Qdrant, Redis, MinIO, ClickHouse, Langfuse
```

#### Layer 1b — Knowledge (LLM Wiki pattern)
```
Obsidian vault (raw .md) → LLM compiles → wiki/ folder → agent queries
Qdrant RAG fallback for overflow/volatile data
```

#### Layer 2 — Inference (Local First, Cloud Fallback)
```
LOCAL (primary — $0):
  Qalb-1.0-8B-Instruct   Urdu conversation, cultural voice (Ollama GPU)
  nomic-embed-text       Embeddings for RAG
  LLaVA 7B               Vision — invoices, camera snapshots
  Whisper STT            Speech-to-text (CPU)
  XTTS-v2-Urdu-FT        Urdu TTS (GPU, on-demand)
  Chatterbox TTS         English TTS (GPU, on-demand)
  Kokoro TTS             English TTS (CPU, always available)
  Frigate YOLO           Object detection on camera feeds

CLOUD (fallback — when local can't handle):
  OpenRouter free        General reasoning, complex tasks ($0)
  OpenRouter paid        Claude Sonnet 4, GPT-4o (frontier)
  ElevenLabs             Urdu TTS quality boost
  Deepgram               Urdu STT accuracy boost
```

#### Layer 3 — Orchestration
```
n8n + 2 workers, Flowise, wassim249 LangGraph agents (hr/finance/legal/sales/ops)
```

#### Layer 4 — MCP & Tools
```
Central MCP Server — tools defined once, used by all agents
```

#### Layer 5 — Voice
```
Asterisk → Dograh → Whisper STT → Bifrost → LLM
→ TTS: XTTS-v2-Urdu-FT (Urdu primary) / Chatterbox (English primary)
       / Kokoro (CPU fallback) — Dograh auto-selects
```

#### Layer D — Lab Intelligence
```
Claude Code Desktop  — AI coding assistant (primary dev tool)
Hermes Agent        — Autonomous 24/7 server ops (Docker)
OpenClaw            — Personal assistant via WhatsApp/Telegram
```

---

## 2b. AI TRANSFORMATION LAYER — 4 USE CASES

Running on top of the Infrastructure Layer — each use case is a standalone
n8n workflow that replaces a manual business process with AI automation:

```
USE CASE 1 — Smart Surveillance
  Cameras → Frigate GPU detection → LLaVA scene analysis
  → MQTT → n8n → WhatsApp alerts to owner
  → PostgreSQL log of all events
  Replaces: security guard monitoring 20 cameras

USE CASE 2 — Smart HR & Payroll
  Face recognition (Ollama + LLaVA) for attendance
  GPS check-in verification + auto timesheets
  Automatic salary calculation + leave management
  Replaces: HR clerk, manual attendance, Excel payroll

USE CASE 3 — Smart Sales CRM
  Meta WhatsApp cloud API → n8n webhook → lead capture
  AI conversation + qualification → Bifrost → Twenty CRM
  Pipeline management + quote generation + follow-up automation
  Replaces: sales assistant, manual lead follow-up

USE CASE 4 — AI Voice Receptionist
  SIP call → Asterisk → Dograh orchestration
  Whisper STT (GPU) → Bifrost → OpenRouter LLM
  Chatterbox TTS (GPU) — primary → voice response (Dograh auto-selects)
  Appointment booking + FAQ + call routing
  Replaces: human receptionist, call center agent
```

Each use case is a self-contained n8n workflow at `/aios/n8n/workflows/` calling Bifrost for inference, logging to Langfuse for observability, and storing data in PostgreSQL + Qdrant.

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
  DDoS protection, SSL certificates, DNS for socialbeesai.com

Layer 2 — TP-Link NAT (port 443 only → Traefik)
  NAT, minimum surface area

Layer 3 — Traefik (DMZ — 10.10.0.10)
  Reverse proxy, HTTPS termination. Public: only Dashy + FOSS apps.
  All internal services: LAN IP:port or WireGuard VPN only.

Layer 4 — CrowdSec (DMZ — 10.10.0.11)
  WAF, IP reputation, rate limiting, brute force detection

Layer 5 — Keycloak (App zone — 10.20.0.40)
   SSO, RBAC, OAuth2/OIDC. Local-only — access via LAN/WireGuard.
```

### 3.3 Docker Network Zones (7 isolated)
```
Zone 1 — DMZ:         10.10.0.0/24   Traefik, CrowdSec
                                       Only zone exposed to internet. Port 443 only.
Zone 2 — Application: 10.20.0.0/24   n8n, Flowise, Dify, Open WebUI, Keycloak,
                                       Vault, FreePBX, WireGuard, Paperclip, Hermes
Zone 3 — Data:        10.30.0.0/24   Supabase, Qdrant, Redis, MinIO
                                       internal:true — NO internet access
Zone 4 — AI:          10.40.0.0/24   Bifrost, Ollama
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

### 3.6 Protocols & Standards
```
Protocol          Standard              Role
────────────────────────────────────────────────────────────
MCP               Anthropic             Standardised tool connections for all agents
A2A               Google                Agent-to-agent communication
OpenTelemetry     CNCF                  Distributed tracing across all services
OAuth2 / OIDC     Industry standard     All auth flows via Keycloak
OpenAI API        De facto LLM standard Bifrost exposes this
MQTT              IoT standard          Frigate event bus to n8n
SIP               Telecoms standard     Asterisk trunking
RTSP              Camera standard       All IP cameras to go2rtc
```

---

## 4. DEVELOPMENT LAYER

### 4.1 Architecture Type
AIOS is a dual-layer system:
- **Infrastructure dev** — Docker Compose configs, n8n workflow JSON, Python scripts, Ansible playbooks, shell scripts
- **Transformation dev** — n8n use-case workflows, Langfuse prompts, Qdrant collections, Bifrost routing, frontend dashboards

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
  Ansible playbooks, Python scripts (backup.py, health-check.py)
  n8n workflow JSON templates
  GitHub Actions CI, Bifrost configs, Traefik rules

EXECUTES ON SERVER:
  docker-compose up -d
  ansible-playbook setup-server.yml
    python3 health-check.py
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
│   ├── health-check.py              # System health verification
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

# Cloud LLMs (via OpenRouter through Bifrost — do NOT call directly)
OPENROUTER_API_KEY=<from Vault>
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
3. Quadro M4000 has 8GB VRAM — no 70B+ locally, routes to OpenRouter/Claude
4. ALWAYS log every LLM call to Langfuse — observability + cost tracking
5. Data Zone (10.30.0.0/24) has internal:true — NEVER change this
6. ALWAYS commit to Git before production changes — Git is source of truth
```

### 4.9 Adding a New Use Case Workflow

```
1. Build/test n8n workflow on the stack
2. HTTP POST → Bifrost → OpenRouter for inference
3. Log to Langfuse for observability + cost tracking
4. Save to /aios/n8n/workflows/{number}-{name}.json
5. git commit + push
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
├── health-check.py         # System health verification
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
Keycloak     10.20.0.40     App          SSO, OAuth2/OIDC
Vault       10.20.0.50     App          Secrets management — ALL API keys
```

### 5.3 AI Core (10.40.0.0/24)
```
Service     IP              Role
────────────────────────────────────────────────────
Bifrost     10.40.0.10      AI Gateway — 4-tier routing (LiteLLM)
Ollama      10.40.0.20      Local GPU — Urdu LLM (Qalb-1.0-8B-Instruct), embeddings (nomic-embed-text), vision (LLaVA 7B)
Chatterbox  10.40.0.30:4123 TTS/voice cloning — GPU (replaces ElevenLabs)
Frigate     10.40.0.50:5000 NVR + YOLO object detection — GPU
```
GPU loaded permanently: Qalb-1.0-8B-Instruct + nomic-embed-text (~5.8GB).
Other models swap on demand via Ollama: XTTS-v2-Urdu-FT, LLaVA 7B, Chatterbox.
CPU always available: Whisper STT, Kokoro TTS.
Frigate YOLO shares GPU for object detection.
ALL text LLM goes through Bifrost: Tier 2 (Qalb local) primary for Urdu, Tier 3 (OpenRouter free) primary for English/general, Tier 4 (OpenRouter paid) for frontier.

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

### 5.5 Voice Layer (10.50.0.0/24 + 10.40.0.0/24 for TTS)
```
Zone    Service     IP              Role
────────────────────────────────────────────────────────────
Voice   Asterisk    10.50.0.10      SIP trunking, call routing, IVR (host net)
Voice   Dograh      10.50.0.30      Voice agent orchestration — replaces Retell AI
Voice   MQTT        10.50.0.20      Event bus — future use
AI      Chatterbox  10.40.0.30:4123 TTS/voice cloning on GPU (primary — Dograh auto-selects)
AI      Kokoro      10.40.0.31:8880 TTS on CPU (fallback — Dograh auto-selects)
```

Voice pipeline: Caller → SIP Trunk → Asterisk → Dograh
  → Whisper STT (local GPU)
  → n8n → Bifrost → OpenRouter → LLM response
  → Dograh auto-selects TTS: Chatterbox (GPU, high quality) or Kokoro (CPU, lighter)
  → Audio back → Asterisk → Caller

### 5.6 Visual AI (App zone)
```
Service     IP              Zone    Role
────────────────────────────────────────────────────────
Frigate     10.20.0.90     App     Real-time object detection (GPU passthrough)
go2rtc      10.20.0.91     App     RTSP stream management
```
Visual pipeline: IP Camera RTSP → go2rtc → Frigate → YOLO → LLaVA description → MQTT → n8n → action

### 5.7 FOSS Business Apps (10.70.0.0/24) — PUBLIC WHEN DEPLOYED
```
App               IP              Role                         Public URL (future)
─────────────────────────────────────────────────────────────────────────────────────
ERPNext           10.70.0.10      Full ERP — hospital, hotel    erpnext.socialbeesai.com
Odoo              10.70.0.20      Full ERP — accounting, CRM    odoo.socialbeesai.com
Twenty CRM        10.70.0.30      Open-source Salesforce alt    twenty.socialbeesai.com
Metabase          10.70.0.40      Business KPI dashboards       metabase.socialbeesai.com
Calcom            10.70.0.50      Appointment scheduling        calcom.socialbeesai.com
SuiteCRM          10.70.0.60      Enterprise CRM                suitecrm.socialbeesai.com
Paperless-ngx     10.70.0.70      Document management           paperless.socialbeesai.com
Docuseal          10.70.0.80      E-signing contracts           docuseal.socialbeesai.com
Planka            10.70.0.90      Project management            planka.socialbeesai.com
Rocket.Chat       10.70.0.100     Team communication            chat.socialbeesai.com
Frappe LMS        10.70.0.110     Learning management           lms.socialbeesai.com
GnuCash           10.70.0.120     Lightweight accounting        (local-only)
```
FOSS apps get public `*.socialbeesai.com` URLs when deployed. All infrastructure/backend services are local-only via LAN IP or WireGuard.

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
Voice calls          Asterisk SIP + Dograh      Audio calls
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
Retell AI / Vapi      REST API        Voice agent platform (REPLACED by Dograh)
Deepgram Nova 3       WebSocket       STT — Arabic/Urdu/English (REPLACED by Whisper local GPU)
TTS (Chatterbox GPU)    REST API  TTS voice cloning — GPU (replaces ElevenLabs)
TTS (Kokoro CPU)        REST API  Lighter TTS — CPU fallback (Dograh auto-selects)
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

## 6. AI LAYER & LLM ROUTING — 4-TIER ARCHITECTURE

### 6.1 AI Gateway — Bifrost (LiteLLM at 10.40.0.10:4000)
ALL LLM calls go through Bifrost. NEVER call APIs directly. Bifrost provides:
- OpenAI-compatible `/v1/chat/completions` endpoint
- 4-tier routing with cross-tier fallback chains
- Semantic caching via Redis (Tier 1 — 50ms, $0)
- Langfuse logging on every call
- Usage-based routing (least-loaded model first)

### 6.2 The 4 Tiers

```
TIER 1 — SEMANTIC CACHE (50ms, $0)
  Bifrost semantic cache via Redis (10.30.0.30)
  similarity_threshold: 0.85, TTL: 3600s
  Hit → return cached response. No LLM call at all.
  40-60% cost savings on repeated queries.

TIER 2 — LOCAL GPU (200ms-2s, $0)
  Ollama on Quadro M4000 (10.40.0.20:11434)
    → Qalb-1.0-8B-Instruct     (Urdu LLM — PRIMARY local conversation model)
    → nomic-embed-text         (embeddings — ALWAYS loaded)
    → LLaVA 7B                 (vision — on-demand)
  Frigate YOLO on GPU                              (object detection)
  Whisper STT on CPU                               (transcription — always available)
  XTTS-v2-Urdu-FT (GPU)                           (Urdu TTS — Dograh auto-selects for Urdu calls)
  Chatterbox TTS (GPU)                             (English TTS — Dograh auto-selects for English calls)
  Kokoro TTS (CPU)                                 (CPU fallback TTS — Dograh auto-selects)

TIER 3 — OPENROUTER FREE (2-8s, $0)
  Primary text LLM — 90%+ of all calls
    → general-reasoning: gemma-4-31b → llama-70b → hermes-405b → nemotron-120b
    → multilingual:      qwen-2.5-72b → gemma-4-31b
    → code:              qwen-coder → deepseek-v4 → gpt-oss-120b
    → fast-simple:       cobuddy → llama-3b → liquid-instruct

TIER 4 — OPENROUTER PAID (3-10s, ~$0.50/1M tokens)
  Frontier models for complex/long-context tasks
    → frontier-reasoning: Claude 4 Sonnet → GPT-4o (via OpenRouter, NOT direct)
    → frontier-vision:    GPT-4o-vision → Claude 4 Sonnet (via OpenRouter)
    → frontier-code:      Claude 4 Sonnet → GPT-4o (via OpenRouter)
```

### 6.3 Task-Based Routing

```
Task                          Primary Route                Fallback Chain
────────────────────────────────────────────────────────────────────────────────────────
Urdu conversation             Tier 2 (Qalb-1.0-8B local)  → Tier 3 (qwen-2.5-72b → gemma-4)
FAQ, classification           Tier 2 (Qalb-1.0-8B local)  → Tier 3 (gemma-4 free)
General reasoning, CRM, HR    Tier 3 (gemma-4-31b free)   → Tier 3 (llama-70b → hermes-405b)
Complex docs, legal, contracts Tier 4 (Claude 4 Sonnet    → Tier 4 (GPT-4o)
                              via OpenRouter paid)
Code generation               Tier 3 (qwen-coder free)    → Tier 3 (deepseek-v4 free)
Vision (images, invoices)     Tier 2 (LLaVA 7B local GPU) → Tier 4 (GPT-4o paid)
STT (voice transcription)     CPU (Whisper always on)     — Deepgram cloud fallback
TTS (voice response)          Tier 2 (XTTS Urdu /          — always local
                              Chatterbox English /               Dograh auto-selects
                              Kokoro CPU fallback)
Embeddings (RAG)              Tier 2 (nomic-embed-text)   — always local
Object detection              Tier 2 (Frigate GPU/YOLO)   — always local
```

### 6.4 Cross-Tier Failure Handling

```
Local GPU down (Tier 2) → OpenRouter free tier takes over (slower but works)
Free tier down          → OpenRouter paid tier takes over (frontier models)
OpenRouter down         → SERVICE DEGRADED — all cloud LLM unavailable
                          (local GPU models + cache still serve)
All tiers failed        → n8n returns graceful error to end user
```

### 6.5 Available Models Reference

```
Model Group            Models (ordered by preference)
────────────────────────────────────────────────────────────────────────
local-urdu             Qalb-1.0-8B-Instruct (Ollama GPU) — PRIMARY
general-reasoning      gemma-4-31b → llama-70b → hermes-405b → nemotron-120b
multilingual           qwen-2.5-72b → gemma-4-31b
code                   qwen-coder → deepseek-v4 → gpt-oss-120b
fast-simple            Qalb-1.0-8B (local) → gemma-4 → llama-3b
frontier-reasoning     Claude 4 Sonnet (OpenRouter paid) → GPT-4o (OpenRouter paid)
frontier-vision        GPT-4o-vision (OpenRouter paid) → Claude 4 Sonnet (OpenRouter paid)
frontier-code          Claude 4 Sonnet (OpenRouter paid) → GPT-4o (OpenRouter paid)
```

### 6.6 Knowledge Layer — LLM Wiki Pattern
```
Layer           Role
────────────────────────────────────────────────────
Obsidian vault  Raw source — client SOPs, pricing, docs, FAQs
LLM compile     Structured markdown wiki (once at ingest)
wiki/ folder    Multi-layered: index, concept, entity, source pages
Agent query     Read compiled wiki at message time
Qdrant RAG      Fallback for overflow/volatile data only
```
Client knowledge bases are small (<50k tokens). LLM Wiki is simpler, cheaper, and more reliable than RAG at this scale. Qdrant reserved for conversations, temp data, cache overflow.

### 6.7 Hybrid Cloud Architecture
```
ON-PREM (never leaves the server):
  Client data, agent memory, conversations, documents
  RAG knowledge bases, business logic, workflow execution
  Camera feeds (Frigate), voice recordings (Asterisk)
  All FOSS app data, vector embeddings (nomic-embed-text)
  TTS voice cloning (Chatterbox), vision (LLaVA), STT (Whisper)

CLOUD (necessary only — all via OpenRouter through Bifrost):
  Text LLM inference — OpenRouter free tier (Tier 3)
  Frontier LLM — OpenRouter paid tier (Tier 4 — Claude/GPT-4o via OpenRouter)
  DNS/SSL — Cloudflare
  Git — GitHub

NOT IN CLOUD (processed locally for privacy/cost):
  Audio streams/recordings — Whisper STT + Chatterbox/Kokoro TTS local
  Camera feeds — Frigate GPU YOLO local
  Client documents — MinIO + Qdrant local
```

---

---

## 8. AI TRANSFORMATION LAYER — 4 USE CASES

These are the **product** — AI Digital Employees running on the AIOS Infrastructure Layer.
Each use case = 1 standalone n8n workflow replacing a manual business process.

```
#   Workflow                  Business Problem Solved       AI Digital Employee
──────────────────────────────────────────────────────────────────────────────────────────
1   03-sales-crm.json         Manual lead follow-up lost   Sales AI Agent
                              revenue. No CRM pipeline.    Manages leads, answers queries,
                              Inconsistent responses.      qualifies, updates Twenty CRM,
                                                           24/7 on WhatsApp.

2   04-voice-receptionist.json  Missed calls = missed      Voice Receptionist AI
                              business. No after-hours     Answers calls, books appointments,
                              coverage. Multi-language     answers FAQs, routes to humans.
                              callers.                     Urdu + English.

3   02-hr-payroll.json        Attendance fraud. Manual     HR & Payroll AI
                              salary calc errors. Leave    Face recognition attendance,
                              tracking chaos.              GPS verification, auto salary,
                                                            leave management.

4   01-surveillance.json      Single guard can't watch     Security AI Agent
                              20 cameras. Alerts missed.   Real-time object detection,
                              No intelligent filtering.    scene understanding, WhatsApp
                                                            alerts to owner.
```

Each workflow at `/aios/n8n/workflows/{number}-{name}.json`, calling Bifrost for inference, logging to Langfuse for cost/observability.

---

## 9. DATA FLOWS

### WhatsApp — Use Case Request Lifecycle
```
End user sends WhatsApp message
→ Meta webhook → Cloudflare → TP-Link NAT → Traefik → CrowdSec
→ n8n webhook endpoint (public path, not full dashboard)
→ n8n workflow (use-case specific — Sales CRM, HR, etc.)
→ Bifrost 4-tier routing (via internal IP 10.40.0.10:4000):
    Tier 1 — Semantic cache check (cached? return immediately, 50ms, $0)
    Tier 2 — Local GPU (Qalb-1.0-8B Urdu LLM on Ollama) — $0
    Tier 3 — OpenRouter free tier (gemma-4, llama-70b, hermes-405b) — $0
    Tier 4 — OpenRouter paid tier (Claude 4 Sonnet, GPT-4o) — if free fails
→ Langfuse logs: prompt + response + cost + latency + tokens + model
→ n8n formats reply → WhatsApp API → end user receives answer
Total: under 3 seconds end-to-end
```
Note: n8n webhook public path TBD — needed when WhatsApp workflow is built.

### Voice Call — Complete Lifecycle
```
Caller dials → SIP trunk → Asterisk (Voice zone — 10.50.0.10)
→ Dograh (local — 10.50.0.30:8000, access via LAN/WireGuard)
  → Whisper STT (CPU — always available)
  → n8n use case workflow
  → Bifrost 4-tier routing → Qalb local / OpenRouter → LLM response
  → TTS: Dograh auto-selects XTTS-v2-Urdu-FT (Urdu, GPU)
         / Chatterbox (English, GPU) / Kokoro (CPU fallback)
→ Audio back → Asterisk → caller
Call recorded. Full transcript logged in Langfuse.
```

### Visual AI — Camera Event Pipeline
```
IP camera RTSP → go2rtc → Frigate (AI zone — 10.40.0.50)
→ YOLO on Quadro M4000 (built into Frigate — detects: person/vehicle/face)
→ LLaVA describes scene via Ollama: "delivery driver at front door"
→ MQTT event (10.50.0.20:1883) → n8n surveillance workflow
→ n8n → Bifrost → LLM decides action → WhatsApp alert
→ Langfuse log + PostgreSQL log
```

### Knowledge Document Ingestion
```
Admin uploads .md / PDF / SOP → Supabase Storage
→ n8n ingestion workflow → LlamaIndex chunks document
→ nomic-embed-text generates vectors → Qdrant stores in knowledge collection
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



---

## 10. PHASES & SCALE PLAN

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

## 11. MARKET CONTEXT

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

## 12. QUICK REFERENCE

### Service Ports (All local-only unless marked PUBLIC)
```
Service           LAN (10.0.0.100)      Docker IP            Public
─────────────────────────────────────────────────────────────────────────
Dashy             8082                   10.60.0.70:8080      socialbeesai.com
n8n               5678                   10.20.0.10:5678      —
Bifrost           4000                   10.40.0.10:4000      —
Langfuse          3000                   10.60.0.10:3000      —
Keycloak          8080                   10.20.0.40:8080      —
Vault             8200                   10.0.0.100:8200      —
Dograh UI         3010                   10.50.0.31:3010      —
Dograh API        8085                   10.50.0.30:8000      —
Frigate           5000                   10.40.0.50:5000      —
MinIO API         9000                   10.30.0.40:9000      —
MinIO Console     9001                   10.30.0.40:9001      —
Grafana           3000                   10.60.0.30:3000      —
Portainer         9000                   10.60.0.50:9000      —
Qdrant            6333                   10.30.0.20:6333      —
ClickHouse        8123                   10.60.0.11:8123      —
Flowise           3001                   10.20.0.20:3000      —
MCP               8100                   10.20.0.30:8000      —
Prometheus        9090                   10.60.0.20:9090      —
Ollama            11434 (localhost only) 10.40.0.20:11434     —
PostgreSQL        5432 (localhost only)  10.30.0.10:5432      —
MQTT              1883                   10.50.0.20:1883      —
Asterisk          SIP (host)             10.50.0.10           —
WireGuard         51820/udp              host                 — (VPN)
```
FOSS apps (Odoo, Twenty CRM, etc.) get public URLs when deployed. All infra = local-only.

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
Server GPU:              Frigate YOLO, LLaVA, Whisper, Chatterbox, nomic-embed
                          nvidia-smi exporter, Ollama (GPU models)
Dev PC:                  Claude Code, OpenClaw, Docker Desktop, WSL2
Cloud APIs:              OpenRouter (200+ models via 4 tiers)
                           Tier 3 — free: llama-70b, gemma-4, hermes-405b, qwen-2.5, deepseek-v4
                           Tier 4 — paid: Claude 4 Sonnet, GPT-4o (via OpenRouter, NOT direct)
                           NO direct API keys — all cloud through OpenRouter gateway
WhatsApp:                Meta Business WhatsApp API
External:                Stripe, JazzCash, AWS (S3/CloudFront/SES), Cloudflare, Twilio
```

### Model Routing Quick Reference
```
Task                          Model                          Reason
────────────────────────────────────────────────────────────────────────
Urdu conversation             Qalb-1.0-8B (Ollama local)     Cultural Urdu voice, $0
Urdu TTS                      XTTS-v2-Urdu-FT (local GPU)    Fine-tuned Urdu voice, $0
English TTS                   Chatterbox (GPU) / Kokoro (CPU) Dograh auto-selects
STT                           Whisper (CPU)                  Always available, $0
General reasoning, CRM, HR    Gemma 4 (OpenRouter free)      Primary — 90%+ calls
Complex docs, legal, long ctx Claude 4 Sonnet (OpenRouter paid) Frontier
Code generation               Qwen Coder (OpenRouter free)   Best free coder
Invoice/image reading         LLaVA 7B (Ollama local)        → GPT-4o paid fallback
Any other model               OpenRouter free tier           25 models up to 405B
Cache hits                    Bifrost semantic cache (Redis) Zero cost
Local down                    OpenRouter free (auto-fallback) Slower but works
Free tier down                OpenRouter paid (Claude/GPT-4o) Frontier fallback
All cloud down                Qalb local only                Degraded — cache still serves
```

---

---

---

## 11. PHASE 1 DELIVERABLES

### Week-by-Week Build Plan — Build AI Infrastructure first, then AI Transformation use cases on top

```
WEEK 1: AIOS Infrastructure Layer — base stack
  Server configured — Docker, GPU, networks
  Docker Layer A (FOSS) + Layer B (AI core) deployed
  All services accessible via Dashy

WEEK 2: AI Transformation — CRM Use Case (#3)
  Build n8n workflow: 03-sales-crm.json
  Wire: webhook → OpenRouter → PostgreSQL → Langfuse
  Test end-to-end via webhook

WEEK 3: AI Transformation — Voice Use Case (#4)
  Wire Asterisk → Dograh → Chatterbox/Kokoro → OpenRouter
  Test call pipeline end-to-end
  Build n8n workflow: 04-voice-receptionist.json

WEEK 4: AI Transformation — HR Use Case (#2)
  Build n8n workflow: 02-hr-payroll.json
  Test GPU vision (face recognition via Ollama/LLaVA)
  Wire payroll logic + GPS

WEEK 5-6: AI Transformation — Surveillance Use Case (#1)
  Connect IP cameras → Frigate → GPU detection
  Build n8n workflow: 01-surveillance.json
  Wire MQTT → n8n → WhatsApp alerts
  Full integration test all 4 use cases
```

### Definition of Done — AI Transformation Use Case
```
✅ n8n workflow in /aios/n8n/workflows/{number}-{name}.json
✅ HTTP POST → Bifrost → OpenRouter for inference
✅ All LLM calls logged to Langfuse
✅ Tested end-to-end with real data via webhook
✅ Functional frontend/dashboard built (Metabase/Streamlit)
```

---

*AIOS PROJECT.md — Complete Reference*
*Version: 4.0 · May 2026 · Lahore AI Lab*
*Infra: 1 Server (Quadro M4000 8GB) · 31GB RAM · 953GB NVMe · TP-Link NAT → Cloudflare*
*~40 Docker containers · 7 network zones · Bifrost AI Gateway · n8n orchestration*
*All decisions locked. Do not modify architecture without updating this document.*
