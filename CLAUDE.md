# AIOS — Claude Code Project Instructions
## Auto-read by Claude Code on every session start

---

## 4-LAYER CONTEXT — Read in this order every session

### Layer 1: AI Rules (this file)
Rules, quick refs, network zones, ports, directory map — keep reading.

### Layer 2: Project Context (loaded on demand)
- `/aios/docs/PROJECT.md` — Complete architecture (v4.0, 16 sections)
- `/aios/docs/ARCHITECTURE_PHILOSOPHY.md` — 7 design principles
- `/aios/docs/SOP.md` — Standard operating procedures
- `/aios/docs/SECURITY.md` — Credential management & rotation

### Layer 3: Session State (always read first)
- `/aios/CHECKPOINT.md` — Current state, completed steps, next plan, known issues

### Layer 4: Resource Inventory (always reference)
- `/aios/docs/INVENTORY.md` — Complete registry of every service, port, credential, volume, dependency

**ALWAYS start by reading CHECKPOINT.md then INVENTORY.md.**

---

## WHO YOU ARE WORKING WITH

Senior IT infrastructure specialist (20+ years). Building a production-grade
AI agency platform in Lahore, Pakistan. This is NOT a hobby project.
Every decision must be production-quality, state-of-the-art, and scalable.

---

## WHAT THIS PROJECT IS — TWO LAYERS

AIOS (AI Operating System) — a 2026-aligned reference architecture for SMB & Enterprise AI transformation:

**Layer 1 — AI Infrastructure (the engine room)**
Best-practice self-hosted AI stack: Docker, GPU, 8 network zones, Bifrost AI Gateway, Langfuse observability, Qdrant vector store, Asterisk voice pipeline, CrowdSec WAF, Traefik reverse proxy, 7-layer architecture. Production-grade, scalable, state-of-the-art.

**Layer 2 — AI Transformation (the product)**
SMB/Enterprise AI Digital Employees running on the infrastructure. 4 prototype use cases: Smart Surveillance, HR & Payroll, Sales CRM, AI Voice Receptionist. Each = a deployable solution replacing manual processes with AI automation.

**Business:** Powers an AI agency in Lahore selling AI Digital Employees to SMBs. Target: Pakistan → UAE → USA markets. 60 clients, PKR 940K MRR by Month 12.

---

## PHYSICAL MACHINES — NEVER CONFUSE THESE

```
SERVER (aios) — 10.0.0.100
  OS: Ubuntu 22.04.5 LTS
  GPU: NVIDIA Quadro M4000 8GB VRAM (Maxwell arch)
  RAM: 31GB DDR4
  Storage: 953GB NVMe
  Runs: Docker Compose Layer A (FOSS apps) + Layer B (AI core)
  Public: NO — via TP-Link NAT + Cloudflare tunnel, port 443 only

DEV PC — 10.0.0.13
  OS: Windows 11 Enterprise
  Role: Development, Docker Desktop for local prototyping
  CPU: Intel Xeon E-2276G @ 3.80GHz (6C/12T)
  RAM: 15.8GB
  Docker: Docker Desktop v29.4.3 — WSL2 backend
```

---

## DIRECTORY STRUCTURE ON SERVER

```
/aios/
├── CLAUDE.md                        # This file
├── docker-compose-aios.yml          # AI core services
├── docker-compose-apps.yml          # FOSS business apps
├── .env.aios                        # AI core secrets (from Vault)
├── .env.apps                        # Apps secrets (from Vault)
├── /ansible/                        # Server setup playbooks
│   ├── inventory.yml
│   ├── setup-server.yml
│   └── /roles/
├── /configs/
│   ├── /traefik/
│   ├── /crowdsec/
│   ├── /keycloak/
│   ├── /bifrost/
│   └── /grafana/
├── /n8n/
│   ├── /workflows/                  # 4 standalone use-case workflows
│   └── /internal/                   # Lab/internal workflows
├── /langfuse/
│   └── /prompts/
├── /scripts/
│   ├── openclaw.py
│   ├── hermes.sh
│   ├── backup.py
│   ├── health-check.py
│   └── disaster-recovery.py
└── /docs/
    ├── PROJECT.md
    ├── CHECKPOINT.md
    ├── DEPLOYMENT_PLAN.md
    └── /capabilities/
```

---

## DOCKER NETWORK ZONES — NEVER BREAK THESE

```
10.10.0.0/24  DMZ Zone         Traefik only — public-facing
10.20.0.0/24  Application Zone n8n, Flowise, Keycloak, Vault
10.30.0.0/24  Data Zone        Supabase, Qdrant, Redis, MinIO
                                internal:true — NO internet access EVER
10.40.0.0/24  AI Zone          Bifrost, Ollama, LiteLLM(dev), Frigate
10.50.0.0/24  Voice Zone       Asterisk, Dograh, MQTT
10.60.0.0/24  Monitoring Zone  Langfuse, Prometheus, Grafana, Loki
10.70.0.0/24  FOSS Zone        ERPNext, Odoo, Twenty CRM, Metabase, Calcom

## KNOWLEDGE LAYER — COMPILED KNOWLEDGE (LLM WIKI PATTERN)

Knowledge is compiled at ingest time, not retrieved at query time:

```
OBSIDIAN VAULT (raw source — client SOPs, pricing, docs, FAQs)
  → LLM compiles structured markdown wiki pages (once at ingest)
  → wiki/ folder (multi-layered: index, concept, entity, source pages)
  → Agent reads compiled wiki at query time
  → Qdrant RAG as fallback for overflow/volatile data

WHY: Client knowledge bases are small (<50k tokens).
     LLM Wiki is simpler, cheaper, and more reliable than RAG for this scale.
     Qdrant reserved for conversations, temp data, cache overflow.
```

## VOICE LAYER — SELF-HOSTED VOICE PIPELINE

```
Asterisk (SIP trunking) — telephony layer
Dograh (voice agent orchestration) — replaces Retell AI/Vapi
  Dograh auto-selects TTS:
    Chatterbox AI (TTS/voice cloning, local GPU) — primary — replaces ElevenLabs
    Kokoro TTS (CPU fallback, lighter/faster) — fallback if GPU busy

Voice pipeline:
  Caller → SIP Trunk → Asterisk → Dograh
    → STT: Whisper (local GPU) or Dograh built-in
    → LLM: Bifrost → OpenRouter
    → TTS: Dograh auto-selects Chatterbox (GPU) or Kokoro (CPU)
  → Audio back → Asterisk → Caller

Text chat pipeline:
  Browser → chat_server.py (10.0.0.100:8081) → Dograh text-chat API (X-API-Key auth)
    → Same Bifrost/frontier-reasoning LLM pipeline
    → Knowledge injected on session creation (address, destinations, pricing)
    → URL: voice.socialbeesai.com/chat (Traefik with stripPrefix)
```
```

---

## SERVICE PORTS — QUICK REFERENCE

```
Bifrost:    http://10.40.0.10:4000  (AI Gateway — ALL LLM calls go here)
n8n:        http://10.20.0.10:5678
Qdrant:     http://10.30.0.20:6333
Flowise:    http://10.20.0.20:3000
MCP Server: http://10.20.0.30:8000
Redis:      redis://10.30.0.30:6379
MinIO:      http://10.30.0.40:9000
Langfuse:   http://10.60.0.10:3000
Grafana:    http://10.60.0.30:3000
Portainer:  http://10.60.0.50:9000
Dashy:      http://10.60.0.70:8080
Prometheus: http://10.60.0.20:9090
Keycloak:   http://10.20.0.40:8080
Vault:      http://10.0.0.100:8200  (host network mode)
Traefik:    http://10.10.0.10:80 / 443 (public)
Asterisk:   http://10.50.0.10 (SIP)
Dograh API: http://10.50.0.30:8000  (voice agent orchestration)
Dograh UI:  http://10.50.0.31:3010  (voice dashboard)
Chatterbox: http://10.40.0.30:4123  (TTS/voice cloning, primary GPU)
Kokoro:     http://10.40.0.31:8880  (TTS, CPU fallback)
MQTT:       http://10.50.0.20:1883
Ollama:     http://10.40.0.20:11434
Frigate:    http://10.40.0.50:5000
ClickHouse: http://10.60.0.11:8123
GitOps:     10.20.0.100            (Auto-deploy — polls GitHub every 30s)
```
- vLLM: NOT DEPLOYED (no GPU VRAM for LLM inference — Quadro only runs Ollama embeddings/vision)
- Supabase: NOT DEPLOYED (only PostgreSQL running)

---

## ABSOLUTE RULES — NEVER VIOLATE

### Rule 1: ALL LLM calls go through Bifrost
```python
# WRONG — never do this
import anthropic
client = anthropic.Anthropic(api_key="sk-...")

# CORRECT — always do this
import requests
response = requests.post(
    "http://10.40.0.10:4000/v1/chat/completions",
    headers={"Authorization": f"Bearer {client_virtual_key}"},
    json={"model": "qwen-2.5-7b", "messages": [...]}
)
```

### Rule 2: NO hardcoded secrets
```bash
# WRONG
ANTHROPIC_API_KEY=sk-ant-xxxxx

# CORRECT — always from Vault or .env
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}  # injected from Vault
```

### Rule 3: Data Zone has internal:true — never remove this
```yaml
# In docker-compose-aios.yml — DO NOT CHANGE
networks:
  data-zone:
    internal: true  # Databases CANNOT reach internet
```

### Rule 4: Inference Server NEVER public
```
# LLM inference runs via Ollama on local Docker AI zone
# NEVER expose Ollama port 11434 to internet
OLLAMA_URL=http://10.40.0.20:11434
# vLLM: NOT DEPLOYED (Quadro M4000 has no VRAM for LLM inference)
```

### Rule 5: Git before production
```bash
# ALWAYS commit before any production change
git add . && git commit -m "description" && git push
# GitOps Agent deploys automatically after push
```

### Rule 6: Always log every LLM call to Langfuse
```
Every call through Bifrost must be logged to Langfuse.
This is how we track cost and observability per use case.
```

---

## MVP v1 ARCHITECTURE — DIRECT USE-CASES (LOCKED May 26)

### Two Layers of AIOS

```
LAYER 1 — AI INFRASTRUCTURE (the engine room)
  7-layer Docker stack: Security → Data → Inference → Orchestration → Voice
  8 network zones (DMZ, App, Data, AI, Voice, Mon, FOSS, Dev)
  Bifrost AI Gateway (all LLM calls), Langfuse (observability + cost tracking)
  Qdrant (vector store), PostgreSQL (relational), Redis (cache)
  Asterisk → Dograh → Whisper → Bifrost → TTS (voice pipeline)
  CrowdSec WAF + Traefik + Cloudflare (security)
  Dashy, Grafana, Portainer (SysOps frontend)

LAYER 2 — AI TRANSFORMATION (the product — runs ON Layer 1)
  4 standalone n8n workflows — each an AI Digital Employee for a business function
    → 01-surveillance:  AI vision + camera feeds → automated security
    → 02-hr-payroll:    Face recognition + GPS → attendance + salary
    → 03-sales-crm:     WhatsApp leads → pipeline → closing
    → 04-voice-receptionist: SIP calls → AI conversation → booking
  Each workflow = self-contained, all logic inline
  Each use case = replaces a manual business process with AI automation
```

### Frontend Architecture — Two Separate Stacks

```
SysOps Frontend (Layer 1 management — IT ops only):
  Dashy, Grafana, Portainer, Prometheus, CrowdSec, Langfuse
  → Manage containers, GPU, network, services, security

Functional Frontend (Layer 2 dashboards — per use case):
  Each use case has its own dashboard + control panel
  → Surveillance: camera grid, alerts timeline, search, visitor counts
  → HR: attendance reports, payroll sheets, leave approvals
  → CRM: lead pipeline, sales performance, invoice follow-ups
  → Voice: call logs, lead captures, appointment calendar
  → Built in Metabase / Streamlit / custom web app per use case
  → NEVER mixed into Dashy or Grafana
```

### Adding a New Use Case (AI Transformation Workflow)

```
1. Build the workflow in n8n — self-contained, all logic in one workflow
2. Node 2 = Set Variables: model, prompt_key, collection_id, etc.
3. HTTP POST → Bifrost → OpenRouter for LLM calls
4. Log every call to Langfuse (observability + cost tracking)
5. Read/write PostgreSQL + Qdrant directly from workflow
6. Test end-to-end with real data
7. Save to: /aios/n8n/workflows/[number]-[name].json
8. Build functional frontend dashboard
9. git commit + push
```

### Scripts Reference

```
/aios/scripts/
├── openclaw.py             # AIOS Lab Assistant — CLI for Dev PC (running)
├── hermes.sh               # 24/7 autonomous ops agent (running)
├── backup.py               # Nightly encrypted backup (TODO)
├── health-check.py         # On-demand health verification (TODO)
├── disaster-recovery.py    # Full system restore (TODO)
```

---

## DEVOPS STACK — WHAT DOES WHAT

```
Claude Code Desktop SSH  → Primary dev tool. SSH to server. Writes + executes everything.
Git + GitHub             → Version control. Source of truth for all configs.
GitHub Actions (on server)→ CI. Validates every push before GitOps deploys.
GitOps Agent (10.20.0.100) → CD. Auto-deploys GitHub changes to Docker stack. Polls every 30s.
Ansible (/aios/ansible/) → Server setup + disaster recovery. Run once per machine.
Hermes Agent (10.20.0.70) → Autonomous 24/7 ops. Monitors + auto-fixes issues.
OpenClaw (on laptop) → Personal assistant. WhatsApp/Telegram interface.
```

### The 7 Non-Negotiable Dev Tools

```
1. Claude Code Desktop — Primary AI dev tool. SSH to server. Writes + executes everything.
2. Git + GitHub        — Version control for ALL configs, workflows, scripts.
3. GitOps Agent        — CD. Auto-deploys GitHub changes to Docker stack. Polls every 30s.
4. Ansible             — Server setup + disaster recovery. Idempotent, unattended.
5. Hermes Agent        — Autonomous 24/7 ops. Monitors, restarts, alerts.
6. OpenClaw            — Personal AI assistant. Inbox, calendar, tasks via WA/Telegram.
7. GitHub Actions CI   — Validation on every push. YAML lint, compose validate, Trivy.
```

### Git Branching Strategy

```
main branch:     production — GitOps Agent deploys from here
dev branch:      staging — test here before promoting to main
feature/* :      new capabilities, new configs

Workflow:
  Create feature branch → Claude Code builds on server
  Push feature → GitHub Actions CI validates
  PR to dev → team reviews
  Test on dev environment
  PR from dev to main → GitOps Agent deploys to production
  If issue → git revert on main → GitOps redeploys
```

### Dev PC Setup (10.0.0.13 — Windows 11)

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
  Node.js server
  Database
  Any AIOS service
```

---

## HOW TO USE THIS PROJECT

### Connect to Server
```bash
# Via Claude Code Desktop SSH (preferred)
# In Claude Code Desktop: SSH → 10.0.0.100

# Via terminal
ssh ai@10.0.0.100

# Via VS Code Remote SSH
# VS Code → Remote SSH → 10.0.0.100
```

### Start AIOS stack
```bash
cd /aios
docker-compose -f docker-compose-aios.yml up -d
docker-compose -f docker-compose-apps.yml up -d
```

### Deploy changes
```bash
git add . && git commit -m "your change" && git push
# GitOps Agent detects and deploys automatically
```

### Run Ansible setup (new server)
```bash
cd /aios/ansible
ansible-playbook -i inventory.yml setup-server.yml
```

### Check system health
```bash
python3 /aios/scripts/health-check.py
# Or visit: http://server-ip/dashy
```

---

## BIFROST ROUTING REFERENCE — 4-TIER TASK-BASED

```
Task                          Primary Route                Fallback Chain
────────────────────────────────────────────────────────────────────────────────────────
FAQ, classification           Tier 2 (Mistral 7B local)    → Tier 3 (gemma-4 free)
Arabic/Urdu conversation      Tier 2 (Qwen 2.5 7B local)   → Tier 3 (qwen-2.5-72b free)
General reasoning, CRM, HR    Tier 3 (gemma-4-31b free)    → Tier 3 (llama-70b) → hermes-405b
Complex docs, legal, contracts Tier 4 (Claude 4 Sonnet     → Tier 4 (GPT-4o)
                              via OpenRouter paid)
Code generation               Tier 3 (qwen-coder free)     → Tier 3 (deepseek-v4 free)
Vision (images, invoices)     Tier 2 (LLaVA 7B local GPU)  → Tier 4 (GPT-4o paid)
STT (voice transcription)     Tier 2 (Whisper local GPU)   — no cloud fallback
TTS (voice response)          Tier 2 (Chatterbox GPU →         — always local
                              Kokoro CPU fallback)              Dograh auto-selects
Embeddings (RAG)              Tier 2 (nomic-embed-text)    — always local
Object detection              Tier 2 (Frigate GPU/YOLO)    — always local

TIERS:
  Tier 1 — Bifrost semantic cache (hit → return, 50ms, $0)
  Tier 2 — Local GPU Ollama (fast Q&A, embeddings, vision, STT, TTS)
  Tier 3 — OpenRouter free tier (primary — 25 free models up to 405B)
  Tier 4 — OpenRouter paid tier (Claude 4 Sonnet, GPT-4o via OpenRouter)
  NO direct API keys — ALL cloud LLM through OpenRouter gateway
```

---

## CISCO 7962G PHONE — FULLY WORKING (May 23)
- MAC: 00:27:0D:C0:1C:92, IP: 10.0.0.12, Ext 9000
- ✅ **Registers** — 9.4.2SR3.1 firmware on TFTP, transport=TCP
- ✅ **Calls OUT** — Cisco dials any extension (100-104)
- ✅ **Incoming calls FIXED** — SEP `transportLayerProtocol=4` (TCP) instead of `2` (UDP). TCP connection stays open, Asterisk sends INVITEs over it.
- SEP: `registerWithProxy=true`, `outboundProxy=10.0.0.100`, `natEnabled=false`, `transportLayerProtocol=4`
- PJSIP: `force_rport=no`, `rewrite_contact=yes`, `disable_rport` must be ABSENT
- `proxy=USECALLMANAGER` is MANDATORY (explicit IP kills REGISTER)
- Full debug: `docs/capabilities/cisco-7962-provisioning.md`

## IMPORTANT CONTEXT

- Founder has 20+ years IT infra experience — do not over-explain basics
- Target market: Pakistan SMBs → UAE → USA/Canada
- Phase 1: 45-day lab setup + 4 prototype use cases
- Phase 2: First clients Month 3, break-even Month 7
- Phase 3: 60 clients, PKR 940K MRR by Month 12
- This is production from Day 1 — not a prototype that gets rebuilt
- The lab IS the product template — clients get same stack minus dev tools
- AIOS = Infrastructure Layer (2026 best-practice) + AI Transformation Layer (use cases)
- Infrastructure = Docker, GPU, 8 zones, Bifrost, Langfuse, Qdrant, Asterisk, Dograh, Chatterbox, Kokoro, CrowdSec, Traefik
- Transformation = 4 AI Digital Employees (Surveillance, HR, CRM, Voice) running ON infrastructure

---

## WHEN IN DOUBT

1. Read PROJECT.md — every decision is documented there
2. Check the Docker network zone before opening any port
3. Check Langfuse before changing any prompt
4. Check Bifrost before adding any LLM call
5. Commit to Git before touching production

*CLAUDE.md — AIOS Project Instructions*
*Version: 4.0 · May 2026 · Lahore AI Lab*
