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

## WHAT THIS PROJECT IS

AIOS (AI Operating System) — a self-hosted hybrid AI platform that:
1. Runs on a single physical server in Lahore
2. Serves as template for client deployments
3. Powers an AI agency selling AI Digital Employees to SMBs
4. Scales to UAE and USA markets

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
├── /clients/
│   └── /[client-id]/
├── /scripts/
│   ├── new-client.py
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
10.40.0.0/24  AI Zone          Bifrost, Ollama(dev), LiteLLM(dev), vLLM
                                Chatterbox AI (TTS, GPU inference)
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
Chatterbox AI (TTS/voice cloning, local GPU) — replaces ElevenLabs

Voice pipeline:
  Caller → SIP Trunk → Asterisk → Dograh
    → STT: Whisper (local GPU) or Dograh built-in
    → LLM: Bifrost → OpenRouter
    → TTS: Chatterbox (local GPU)
  → Audio back → Asterisk → Caller
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
Chatterbox: http://10.40.0.30:4123  (TTS/voice cloning, GPU)
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

### Rule 5: All client resources via new-client.py only
```bash
# CORRECT
python3 /aios/scripts/new-client.py --client-id clinic-abc --industry clinic

# NEVER create Keycloak/Qdrant/Supabase/Bifrost resources manually
```

### Rule 6: Git before production
```bash
# ALWAYS commit before any production change
git add . && git commit -m "description" && git push
# GitOps Agent deploys automatically after push
```

### Rule 7: n8n workflows — ALL client data as variables
```json
// WRONG — hardcoded client
{"collection_id": "clinic-abc-knowledge"}

// CORRECT — variable from Node 2
{"collection_id": "{{$node.SetVariables.json.collection_id}}"}
```

### Rule 8: Always enforce Supabase RLS
```sql
-- Every table must have this
ALTER TABLE [table_name] ENABLE ROW LEVEL SECURITY;
ALTER TABLE [table_name] FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON [table_name]
  USING (schema_name = current_setting('app.tenant_id'));
```

### Rule 9: Always log every LLM call to Langfuse
```
Every call through Bifrost must be logged to Langfuse.
This is how per-client billing is calculated.
```

---

## MULTI-TENANT ISOLATION — v2 (NOT IN MVP v1)

MVP v1 runs direct use cases on the stack — no client isolation layer.
Multi-tenant model is postponed to v2 when we onboard actual clients.

```
Future v2 isolation per client:
  Keycloak:  One Organization per client (Keycloak 26 Organizations feature)
  Qdrant:    One collection per client — named {client_id}-knowledge
  Supabase:  One schema per client — named {client_id} with RLS enforced
  Bifrost:   One virtual key per client — with monthly budget limit
  n8n:       One main workflow per client — tagged with client_id
  Langfuse:  One project per client — for cost tracking + prompts
  Paperclip: One company per client — agents, budgets, org chart
```

---

## MVP v1 ARCHITECTURE — DIRECT USE-CASES (LOCKED May 26)

### Decision: No capability abstraction layer
Capabilities (reusable n8n sub-workflows) are REMOVED from MVP v1.
Instead, build 4-5 real business use cases as standalone n8n workflows
running directly on the AIOS stack. No test client layer.

### Why
- MVP v1 is a prototype — we validate use cases, not abstractions
- Capability layer adds complexity before we know what works
- Real use cases on real stack = faster iteration, real feedback
- Client isolation model can be added in v2 when we onboard actual clients

### Structure
```
/aios/n8n/workflows/
├── 01-surveillance.json           # Smart AI Surveillance & Security
│                                  #   Frigate NVR → GPU vision → n8n alerts → WhatsApp
├── 02-hr-payroll.json             # Smart HR Attendance & Payroll
│                                  #   Face recognition + GPS + auto salary + leave mgmt
├── 03-sales-crm.json              # Smart Sales CRM & Customer Management
│                                  #   Leads → WhatsApp CRM → pipeline → dashboard
├── 04-voice-receptionist.json     # AI Voice Receptionist & Call Center Agent
│                                  #   Asterisk → Dograh → STT → LLM → TTS → callback
└── internal/                      # Lab/internal workflows
```

### Frontend Architecture — Two Separate Stacks

```
SysOps Frontend (infrastructure — US only):
  Dashy, Grafana, Portainer, Prometheus, CrowdSec, Langfuse
  → AIOS operators manage containers, GPU, network, services
  → NEVER expose client UIs here

Functional Frontend (business — per use case, for END CLIENTS):
  Each use case has its own dashboard + control panel
  → Surveillance: camera grid, alerts timeline, search, visitor counts
  → HR: attendance reports, payroll sheets, leave approvals
  → CRM: lead pipeline, sales performance, invoice follow-ups
  → Voice: call logs, lead captures, appointment calendar
  → Built in Metabase / Streamlit / custom web app per use case
  → NEVER mixed into Dashy or Grafana
```

### Adding a New Use Case (Direct Workflow)

```
1. Build the workflow in n8n — self-contained, all logic in one workflow
2. Node 2 = Set Variables: model, prompt_key, collection_id, etc.
3. HTTP POST node → OpenRouter for LLM calls
4. Log every call to Langfuse (observability + cost tracking)
5. Read/write PostgreSQL + Qdrant directly from workflow
6. Test end-to-end with real data
7. Save to: /aios/n8n/workflows/[number]-[name].json
8. Build functional frontend for end-client dashboard
9. git commit + push
```

### Scripts Reference

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

### Onboard new client
```bash
python3 /aios/scripts/new-client.py \
  --client-id clinic-abc \
  --industry clinic \
  --language urdu \
  --model qwen-2.5-7b \
  --budget 50 \
  --agent-name Sarah \
  --whatsapp +923001234567
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

## BIFROST ROUTING REFERENCE

```
Task                          Model                          Reason
────────────────────────────────────────────────────────────────────────
Simple FAQ, classification    Mistral 7B (vLLM)              Fast + free
Arabic/Urdu conversation      Qwen 2.5 7B (vLLM)            Best multilingual local
General reasoning, HR tasks   Llama 3 8B (vLLM)             High quality, zero cost
General reasoning (API)       openrouter-free               Routes to best free model
Heavy reasoning, long ctx     gemma-4-31b / llama-70b       $0, free tier
Complex code, structured      qwen-coder / gpt-oss-120b     $0, best coding free models
Fast/simple Q&A               cobuddy / llama-3b / owl-alpha $0, fast + light
Frontier reasoning (405B)     hermes-405b / nemotron-120b    $0, massive models
Invoice/image reading         Not available (paid only)     Free tier has no vision models
Any other need                openrouter-free               Routes to best available free model
Local models down/busy        openrouter-free               Multi-tier auto-fallback
70B+ reasoning                llama-70b / hermes-405b       $0 free tier — plenty of power
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

---

## WHEN IN DOUBT

1. Read PROJECT.md — every decision is documented there
2. Check the Docker network zone before opening any port
3. Check Langfuse before changing any prompt
4. Check Bifrost before adding any LLM call
5. Run new-client.py before creating any client resources manually
6. Commit to Git before touching production

*CLAUDE.md — AIOS Project Instructions*
*Version: 4.0 · May 2026 · Lahore AI Lab*
