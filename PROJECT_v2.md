# AIOS — AI Operating System
## 2026 Reference Architecture for SMB & Enterprise AI Transformation
### Lahore AI Lab · June 2026

---

## 1. PROJECT OVERVIEW — TWO LAYERS

### Layer 1: AI Infrastructure (the engine room)
Best-practice self-hosted AI stack — 7 Docker layers, 8 network zones, GPU passthrough.
Production-grade, scalable, state-of-the-art AI infrastructure.

### Layer 2: AI Transformation (the product)
SMB/Enterprise AI Digital Employees running ON the infrastructure.
4 use cases replacing manual business processes with AI automation.

### What This Is
AIOS (AI Operating System) is a 2026-aligned reference architecture that combines:

1. **Infrastructure Layer** — Docker, GPU, Bifrost, Langfuse, Qdrant, Asterisk, Dograh, Chatterbox, CrowdSec, Traefik — best-practice self-hosted AI stack
2. **Transformation Layer** — 4 AI Digital Employees (Surveillance, HR, CRM, Voice) running as n8n workflows on the infrastructure

### Business Context
- **Founder:** Senior IT infrastructure specialist, 20+ years experience, documented government-scale AI transformation (38,000-school SED deployment)
- **Business model:** Sell AI Digital Employees (Transformation Layer use cases) to SMBs, running on the AIOS Infrastructure Layer
- **Target markets:** Pakistan (Lahore) → UAE (Dubai/Abu Dhabi) → USA/Canada (white-label)
- **Revenue model:** PKR 35–75K setup fee + PKR 12–22K monthly recurring per use case per client
- **Target:** 60 clients by Month 12, PKR 940K MRR

### Core Principle
The lab IS the product. What is built and tested here is exactly what gets deployed for clients. When a client signs — no new infrastructure is built. Only configuration is added on top of the existing stack.

---

## 2. PHYSICAL INFRASTRUCTURE — FINAL LOCKED

### IMPORTANT: 2 Physical Machines Only. No Third Machine.

---

### Machine 1 — Workstation 1 (WS1)
```
OS:       Ubuntu 24.04 LTS
Role:     Primary server — KVM hypervisor + Docker services
IP:       192.168.1.10 (LAN) / 10.70.0.1 (WireGuard)
Public:   YES — port 443 only via Cloudflare + OPNsense + Traefik
GPU:      RTX 4090 24GB VRAM — dev inference + AI Docker services
RAM:      64GB DDR5
Storage:  2TB NVMe + 4TB HDD
```

**WS1 has 4 layers running simultaneously:**

#### Layer 1 — KVM Hypervisor (system-level VMs)
```
KVM VM 1: OPNsense
  OS:       FreeBSD (OPNsense native)
  RAM:      2GB
  Disk:     20GB NVMe
  Role:     Network perimeter firewall — routing, VLAN, IDS/IPS (Suricata),
            WireGuard VPN, NAT, DNS filtering
  Network:  Bridged — sits between WAN and LAN

KVM VM 2: Issabel
  OS:       AlmaLinux 9
  RAM:      4GB
  Disk:     80GB NVMe
  Role:     Full UC platform — call centre GUI, voicemail, IVR builder,
            call recordings, real-time monitoring, reporting dashboards.
            Built on Asterisk. SIP trunked to Asterisk Docker container.
  Network:  Internal LAN — SIP trunk to Asterisk Docker on WS1
```

#### Layer 2 — Docker Compose A (FOSS non-AI business apps)
Separate `docker-compose-apps.yml` file. Independent lifecycle from AI stack.
```
Odoo, ERPNext/Frappe, Twenty CRM, SuiteCRM, Calcom, Paperless-ngx,
Docuseal, Planka, Rocket.Chat, Frappe LMS, GnuCash, Metabase
```

#### Layer 3 — Docker Compose B (AI core services — AIOS engine)
Separate `docker-compose-aios.yml` file. This is the AIOS engine.
```
Traefik, CrowdSec, Keycloak, HashiCorp Vault, Bifrost AI Gateway,
Ollama (dev only), LiteLLM (dev only), MQTT Broker, Asterisk PBX,
n8n + workers, Flowise, Dify, Paperclip, Hermes Agent, Langfuse,
Qdrant, Supabase (Postgres), Redis, MinIO, Open WebUI,
Grafana, Prometheus, Loki, Portainer, Dashy, Uptime Kuma, Dozzle,
ArgoCD, Watchtower, Trivy
```

#### Layer 4 — Internal Lab Intelligence (installed directly, not Docker)
```
Claude Code    — AI coding assistant (Anthropic subscription)
OpenClaw       — Personal AI assistant via WhatsApp/Telegram
```

---

### Machine 2 — Inference Server
```
OS:       Ubuntu 24.04 LTS — bare metal only
Role:     Dedicated GPU compute — vLLM + Frigate + visual AI
IP:       192.168.1.20 (LAN) / 10.70.0.2 (WireGuard)
Public:   NEVER — internal LAN + WireGuard tunnel to WS1 only
GPU:      2× RTX 3090 24GB VRAM each — dedicated LLM serving + visual AI
RAM:      128GB DDR4
Storage:  4TB NVMe + 8TB HDD + NAS 4-bay 8TB
KVM:      NONE — bare metal only, direct GPU access for max throughput
FOSS:     NONE — pure AI compute only
```

**Inference Server Docker Compose (single file):**
```
vLLM, Frigate NVR, LLaVA 7B, YOLOv9 (TensorRT), go2rtc,
nvidia-smi Prometheus exporter
```

**GPU allocation:**
```
RTX 3090 #1:  vLLM — Llama 3.1 70B Q4 + Mistral 7B
RTX 3090 #2:  vLLM — Qwen 2.5 72B + Frigate/YOLOv9
```

---

### WS1 Resource Allocation
```
KVM OPNsense VM:     2GB RAM  | 2 vCPU  | 20GB NVMe
KVM Issabel VM:      4GB RAM  | 4 vCPU  | 80GB NVMe
Docker Layer A:     16GB RAM  | 4 vCPU  | 400GB NVMe
Docker Layer B:     32GB RAM  | 8 vCPU  | 1.5TB NVMe  | RTX 4090
Total:              54GB/64GB | 18 vCPU | 2TB NVMe
```

---

## 3. NETWORK ARCHITECTURE

### Physical Network
```
Internet → Cloudflare → OPNsense (WS1 KVM) → LAN Switch
  WS1:              192.168.1.10
  Inference Server: 192.168.1.20
  WireGuard overlay: 10.70.0.0/24
```

### WireGuard Overlay (cross-machine private tunnel)
```
WS1:              10.70.0.1
Inference Server: 10.70.0.2
```
Note: OPNsense manages WireGuard — replaces standalone WireGuard container.

### Security Layer Order (5 layers — traffic passes all in sequence)
```
1. Cloudflare        — cloud edge: DDoS, SSL certificates, CDN
2. OPNsense (KVM)    — network perimeter: firewall, IDS/IPS Suricata, VLAN, WireGuard
3. Traefik           — reverse proxy: HTTPS termination, container routing
4. CrowdSec          — WAF: IP reputation, rate limiting, brute force protection
5. Keycloak          — identity: tenant auth, RBAC, OAuth2/OIDC
```

### Docker Network Zones (7 isolated zones)
```
Zone 1 - DMZ:         10.10.0.0/24  — Traefik (10.10.0.10), CrowdSec (10.10.0.11)
                                        Only zone exposed to internet. Port 443 only.
Zone 2 - Application: 10.20.0.0/24  — n8n (.10/.11/.12), Flowise (.20), Dify (.21),
                                        Open WebUI (.30), Keycloak (.40), Vault (.50)
Zone 3 - Data:        10.30.0.0/24  — Supabase (.10), Qdrant (.20), Redis (.30),
                                        MinIO (.40). internal:true — NO internet access.
Zone 4 - AI:          10.40.0.0/24  — Bifrost (.10), Ollama dev (.20), LiteLLM dev (.30),
                                        vLLM Inference Server (.40 via WireGuard)
Zone 5 - Voice:       10.50.0.0/24  — Asterisk (.10), MQTT Broker (.20)
Zone 6 - Monitoring:  10.60.0.0/24  — Langfuse (.10), Prometheus (.20), Grafana (.30),
                                        Loki (.40), Portainer (.50), Uptime Kuma (.60),
                                        Dashy (.70), Dozzle (.80)
Zone 7 - Cross-machine: 10.70.0.0/24 — WireGuard tunnel: WS1 (.1) ↔ Inference Server (.2)
```



---

## 4. AIOS ARCHITECTURE — ALL TIERS

### TIER 1 — INPUT CHANNELS
How requests enter the system.

```
Channel             Tool / Protocol              What It Carries
─────────────────────────────────────────────────────────────────
Voice calls         Asterisk SIP + Retell AI     Audio calls
WhatsApp            Meta WhatsApp Business API   Text, images, voice notes, docs
Web chat            React widget + n8n webhook   Text conversations
REST API/Webhooks   n8n webhook nodes            External triggers, form submissions
IP Cameras          RTSP → go2rtc → Frigate      Live video feeds
Document upload     Supabase Storage + n8n       PDFs, invoices, contracts, images
Email inbound       IMAP/SMTP via n8n            Email triggers, attachments
SMS                 Twilio                       Alerts, reminders, OTPs
```

---

### TIER 2 — SECURITY, WAF & IDENTITY
```
Tool                Where           Role
──────────────────────────────────────────────────────────────────
Cloudflare          Cloud           Edge DDoS, DNS, SSL, CDN
OPNsense            WS1 KVM VM      Network firewall, IDS/IPS (Suricata), WireGuard, VLAN
Traefik             WS1 Docker B    Reverse proxy, HTTPS termination, load balancing
CrowdSec            WS1 Docker B    WAF, IP reputation, rate limiting, brute force
Keycloak            WS1 Docker B    SSO, RBAC, OAuth2/OIDC
HashiCorp Vault     WS1 Docker B    All API keys encrypted at rest, injected at runtime
Docker networks     WS1             7-zone isolation, internal:true on data zone
```

---

### TIER 3 — AI GATEWAY & LLM INTELLIGENCE

#### Production AI Gateway
```
Tool       Where           Role
────────────────────────────────────────────────────────────────────────
Bifrost    WS1 Docker B    PRODUCTION gateway — 11μs overhead, 5000+ RPS,
                           semantic caching (40-60% cost saving), per-client
                           virtual keys, budget controls, MCP support,
                           automatic failover, prompt injection detection,
                           PII sanitisation, OpenAI-compatible API endpoint.
LiteLLM    WS1 Docker B    DEV/PROTOTYPE ONLY — not in production client path.
                           Used by developers for testing new integrations.
```

#### Local LLM Inference — Production (Inference Server)
```
Tool              Where                   Role
──────────────────────────────────────────────────────────────────────
vLLM              Inference Server        Production inference engine.
                  Docker                  OpenAI-compatible API on port 8000.
                                         Serves all local models on RTX 3090s.
Llama 3.1 70B Q4  RTX 3090 #1            General reasoning, agent tasks, docs
Mistral 7B        RTX 3090 #1            Fast lightweight tasks, high throughput
Qwen 2.5 72B      RTX 3090 #2            Arabic + Urdu + English multilingual
LLaVA 7B          RTX 3090 #2            Visual LLM — reads images, invoices
Ollama            WS1 Docker B           DEV ONLY — testing and prototyping
```

#### Cloud LLMs (via Bifrost gateway)
```
Model                 Provider    Role
─────────────────────────────────────────────────────────────────
Claude 4 Sonnet API   Anthropic   Complex reasoning, long docs, agentic tasks
GPT-4o API            OpenAI      Vision tasks, structured extraction, fallback
Gemini 2.0 API        Google      Multimodal fallback, long context
```

#### Bifrost Routing Logic
```
Task Type                           Routes To                    Reason
──────────────────────────────────────────────────────────────────────────
Simple FAQ, routing, classification  Mistral 7B (local vLLM)      Fast, free
Arabic/Urdu conversation             Qwen 2.5 72B (local vLLM)    Best multilingual
General reasoning, HR, inventory     Llama 3.1 70B (local vLLM)   High quality, zero cost
Complex docs, legal, long context    Claude 4 Sonnet (API)        Frontier quality needed
Invoice/image reading                GPT-4o (API) + LLaVA (local) Best vision models
Local models under load/down         Claude API (auto-failover)    Zero downtime
Cached/repeated queries              Bifrost semantic cache        No LLM call at all
```

#### Central Prompt Registry + RAG Pipeline
```
Tool              Where           Role
──────────────────────────────────────────────────────────────────
Langfuse          WS1 Docker B    ALL agent system prompts stored, versioned,
                                  managed centrally. Agents pull at runtime.
                                  Change once — all agents update instantly.
nomic-embed-text  WS1 (Ollama)    Embedding model — converts docs to vectors
LlamaIndex        WS1 Docker B    Document chunking + RAG pipeline processing
```

---

### TIER 4 — VISUAL AI (Frigate Pipeline)
```
Tool              Where                   Role
──────────────────────────────────────────────────────────────────────
Frigate 0.17 NVR  Inference Server        Realtime AI object detection on IP
                  Docker                  camera RTSP feeds. People, vehicles,
                                         faces, licence plates. GPU-accelerated.
YOLOv9 TensorRT   RTX 3090 #2            Object detection model — GPU-accelerated
LLaVA 7B          RTX 3090 #2            Natural language descriptions of events
go2rtc            Inference Server        IP camera RTSP stream management
MQTT Broker       WS1 Docker B           Event bus: Frigate event → n8n workflow
```

**Visual AI Pipeline:**
```
IP Camera RTSP → go2rtc → Frigate → YOLOv9 (detects object)
→ LLaVA (describes: "delivery driver at front door")
→ MQTT event → n8n workflow fires → action taken
```

---

### TIER 5 — VOICE AI

**IMPORTANT: Asterisk is a Docker container on WS1. Issabel is a KVM VM on WS1. They are SIP trunked together. This is standard telecoms architecture.**

```
Tool              Where               Role
──────────────────────────────────────────────────────────────────────
Asterisk PBX      WS1 Docker B        Core VoIP engine — SIP trunking, PSTN
                                      connectivity, call routing, IVR, extensions,
                                      call recording. AI voice pipeline runs here.
Issabel           WS1 KVM VM          Full call centre management GUI built on
                                      Asterisk. Dashboards, recordings, voicemail,
                                      IVR builder, real-time monitoring, reporting.
                                      SIP trunked to Asterisk Docker container.
Retell AI / Vapi  Cloud API           Voice agent platform — conversation
                                      orchestration, interruptions, turn-taking
Deepgram Nova 3   Cloud API           STT — $0.0077/min. Arabic+Urdu+English.
ElevenLabs        Cloud API           TTS — $22/mo Creator. 29+ languages.
```

**Voice Pipeline Flow:**
```
Caller dials → Issabel (GUI + dashboard) → SIP trunk → Asterisk (WS1 Docker)
→ Retell AI / Vapi → Deepgram STT → n8n workflow → Bifrost → vLLM / Claude
→ ElevenLabs TTS → audio back → Asterisk → Issabel → caller
```

---

### TIER 6 — AUTONOMOUS AGENT & WORKFLOW ORCHESTRATION

#### Master Orchestration
```
Tool              Where           Role
──────────────────────────────────────────────────────────────────────
n8n (queue mode)  WS1 Docker B    Master orchestrator — ALL business logic,
                                  ALL client agent workflows, 1,400+ integrations.
                                  Redis queue mode for parallel execution.
n8n worker ×2     WS1 Docker B    Stateless workers pulling from Redis queue.
                                  Add more workers as client load grows.
Flowise           WS1 Docker B    Visual no-code agent chain builder.
                                  Rapid prototyping of new use case agents.
Dify              WS1 Docker B    LLM app platform — visual workflow builder,
                                  RAG management UI, API publishing.
```

#### Multi-Agent Framework
```
Tool              Where           Role
──────────────────────────────────────────────────────────────────────
CrewAI            WS1 Docker B    Python multi-agent coordination — specialist
                                  agents coordinating on complex tasks
LangGraph         WS1 Docker B    Stateful graph-based agent workflows —
                                  complex multi-step reasoning with loops
A2A Protocol      WS1             Agent-to-agent communication standard (Google)
MCP               WS1             Model Context Protocol — standardised tool
                                  connections for all agents (Anthropic)
```

#### Agent Patterns
```
Pattern           When Used                           Example
────────────────────────────────────────────────────────────────────
ReAct             Dynamic tasks, unpredictable path    Lead qualification
Plan-and-Execute  Predictable workflow, clear steps    Invoice processing
Multi-agent       Complex multi-domain tasks           HR onboarding
Human-in-loop     High-stakes decisions               Legal document review
```

#### Agent Governance
```
Tool              Where           Role
──────────────────────────────────────────────────────────────────────
Paperclip         WS1 Docker B    AI company OS — manages ALL agents across
                                  ALL companies. Org chart, goals, budgets,
                                  heartbeats, tickets, audit trail.
                                  Connects to Bifrost via OpenAI-compatible API.
                                  Multi-company: YOUR company + each client company.
Langfuse          WS1 Docker B    Prompt registry + LLM observability.
                                  Every LLM call logged — cost, tokens, latency.
                                  Full evaluation framework for agent quality.
```

#### Paperclip — Company Structure
```
YOUR lab Paperclip company (internal ops only):
  ├── Claude Code agent   — builds n8n workflows and use cases
  ├── Hermes agent        — DevOps, server management, automation
  ├── OpenClaw           — your personal assistant
  └── Research agents, content agents, reporting agents

Each CLIENT Paperclip company (business ops only):
  ├── Their receptionist agent
  ├── Their HR agent
  ├── Their reporting agent
  └── Their industry-specific agents
  NOTE: NO dev agents, NO Hermes, NO Claude Code in client companies
```

#### Paperclip ↔ n8n Integration
```
Paperclip → HTTP POST → n8n webhook → n8n workflow executes → result back to Paperclip
RULE: Paperclip only triggers YOUR INTERNAL n8n workflows.
      Client-facing agents are event-driven (WhatsApp/voice webhooks) — NOT Paperclip heartbeats.
```

---

### INTERNAL LAB INTELLIGENCE LAYER
Your team's AI tools. Never deployed to clients.

```
Tool          Where               Role
──────────────────────────────────────────────────────────────────────
Claude Code   WS1 terminal        AI coding assistant — reads entire repos,
                                  executes commands, builds use cases 3–5× faster.
                                  PRIMARY development tool for all engineers.
Hermes Agent  WS1 Docker B        Autonomous technical agent — DevOps automation,
                                  server management, research, coding automation.
                                  Has web dashboard at port 9119.
OpenClaw      WS1 installed       Personal AI assistant — manages YOUR inbox,
                                  calendar, tasks via WhatsApp/Telegram.
                                  Can optionally be given to tech-savvy clients.
Paperclip     WS1 Docker B        Manages Claude Code, Hermes, OpenClaw as a
              (shared with         coordinated team. Org chart, budgets, heartbeats.
               client layer)
```

---

### TIER 7 — DATA & MEMORY

```
Tool              Where                   Role
──────────────────────────────────────────────────────────────────────
Qdrant            WS1 Docker B            Vector DB — one collection per client.
                                          All RAG knowledge bases, SOPs, FAQs,
                                          .md skills files. Semantic search.
Supabase          WS1 Docker B            Operational DB — agent memory, conversation
(Postgres)                                history, CRM data, user records, reports,
                                          prompt versions. Per-client schema + RLS.
Redis             WS1 Docker B            n8n queue (queue mode), session cache,
                                          conversation context, short-term memory.
MinIO             WS1 Docker B            Self-hosted S3-compatible object storage —
                                          client docs, model files, Frigate recordings.
NAS 4-bay 8TB     Inference Server rack   vLLM model files, datasets, Frigate video,
                                          backups. Mounted via NFS to both machines.
AWS S3            Cloud (hybrid)          Nightly offsite backup — Postgres dumps,
                                          Qdrant snapshots, n8n exports. Disaster recovery.
```

---

### TIER 8 — INTEGRATIONS & FOSS BUSINESS APPS

#### Self-Hosted FOSS Apps (Docker Layer A on WS1)
```
App               Role
──────────────────────────────────────────────────────────────────────
Odoo              Full ERP — inventory, accounting, HR, CRM, purchasing
ERPNext / Frappe  Full ERP + verticals — Hospital, Hotel, Restaurant,
                  Manufacturing, LMS, Education modules
Twenty CRM        Modern open-source Salesforce alternative
SuiteCRM          Full enterprise CRM — campaigns, cases, reports
Calcom            Open-source booking — appointment scheduling
Paperless-ngx     Document management — OCR, tagging, archiving
Docuseal          FOSS e-signing — contracts via n8n workflow
Planka            Project management (Trello-like)
Rocket.Chat       Team communication (Slack alternative)
Frappe LMS        Learning management — courses, assessments, certificates
GnuCash           Lightweight accounting for small firms
Metabase          Client-facing business dashboards (primary)
```

#### Industry-Specific App Deployments
```
Industry              Primary FOSS App
──────────────────────────────────────────────
Clinic / Healthcare   ERPNext Hospital
Real Estate           Twenty CRM + Calcom + Docuseal
Retail / Pharmacy     ERPNext POS + Inventory
Restaurant            ERPNext POS + Frappe Restaurant
Hotel / Hospitality   ERPNext Hotel
Academy / Education   Frappe LMS + ERPNext Education
Legal / Accounting    Paperless-ngx + Docuseal + GnuCash
Manufacturing         ERPNext Manufacturing
NGO / Government      ERPNext + Paperless-ngx
HR & Payroll          ERPNext HR Module
```

#### External Integrations (via n8n + MCP)
```
Integration           Protocol        Use Case
──────────────────────────────────────────────────────────────────
WhatsApp Business API Meta webhook    All WhatsApp agents
Twilio                REST API        SMS alerts, voice backup, OTPs
Google Calendar       OAuth → n8n     Appointment booking agents
Microsoft 365         OAuth → n8n     Enterprise client integrations
JazzCash / EasyPaisa  REST API        Pakistan payments
Stripe                REST API        UAE / US payments
MCP servers           Anthropic MCP   Standardised tool connections
```

---

### TIER 9 — DASHBOARDS & ANALYTICS

#### SysOps Dashboards (YOUR team only)
```
Tool              Role
──────────────────────────────────────────────────────────────────────
Dashy             Central navigation homepage — single URL linking ALL admin
                  tools with live status indicators. Your team's daily start page.
Grafana           Single pane of glass — infra metrics, GPU VRAM, LLM costs,
                  agent performance. Also exposes per-client Grafana organisations
                  for tech-savvy clients.
Prometheus        Raw metrics from all machines — CPU, RAM, disk, network,
                  GPU temperature, VRAM usage, container resource usage
Loki              Centralised log aggregation — all containers, searchable from Grafana
Dozzle            Real-time Docker log viewer — live, colour-coded per container
Uptime Kuma       Every service monitored — alerts to WhatsApp via n8n
Portainer         Docker container management — start/stop/update/inspect/terminal
Langfuse          LLM observability — every call logged, cost per client, latency,
                  tokens, prompt versions, evaluation scores
OpenTelemetry     Distributed tracing — follows every agent request across all tiers
Bifrost dashboard Per-client API costs, cache hit rate, model routing, budget
n8n dashboard     All workflows, execution history, error logs, trigger status
Paperclip admin   All agent companies, org charts, budgets, tickets, audit trail
Hermes dashboard  Internal DevOps agent — sessions, cron jobs, logs (port 9119)
CrowdSec          Blocked IPs, attack patterns, threat intelligence
Keycloak admin    All tenants, users, login attempts, access audit
Issabel           Call recordings, duration, missed calls, queue stats, IVR
MinIO console     Stored objects, buckets, storage usage, access logs
```

#### Functional Dashboards (SMB clients)
```
Tool                    Role
──────────────────────────────────────────────────────────────────────
Metabase                PRIMARY client dashboard — business KPIs, use case
                        metrics, ROI data. Non-technical. Per-client isolated.
React + Supabase portal Custom white-label client portal — branded per client
n8n reporting agents    Auto-generated daily/weekly/monthly reports →
                        delivered to client WhatsApp or email automatically
Grafana (client org)    For tech-savvy clients — own Grafana organisation,
                        their data only
Paperclip console       Optional for advanced clients — see their agents,
                        budgets, tasks
```

---

### TIER 10 — SYSOPS, CI/CD & OBSERVABILITY

```
Tool              Where           Role
──────────────────────────────────────────────────────────────────────
Portainer         WS1 Docker B    Docker container management UI — both machines
Prometheus        WS1 Docker B    Metrics collection from all machines
Grafana           WS1 Docker B    Unified visualization — infra + LLM + business
Loki              WS1 Docker B    Centralised log aggregation
OpenTelemetry     WS1             Distributed tracing — CNCF standard
Langfuse          WS1 Docker B    LLM observability + prompt registry
Uptime Kuma       WS1 Docker B    Service uptime — alerts to WhatsApp
Dozzle            WS1 Docker B    Real-time Docker log viewer
Dashy             WS1 Docker B    Central navigation homepage
ArgoCD            WS1 Docker B    GitOps CI/CD — push to GitHub → auto-deploy
Watchtower        WS1 Docker B    Auto-updates Docker containers on new images
Trivy             WS1 Docker B    Container security scanning before deployment
nvidia-smi exp.   Both machines   GPU metrics — VRAM, temp, utilisation
Automated backup  Both + cloud    Nightly: pg_dump + Qdrant + n8n → NAS → S3
```

---

## 5. HYBRID CLOUD ARCHITECTURE

### 3 Zones

#### Zone 1 — On-Premise (primary workloads)
Everything primary runs on-prem:
- All client data (Supabase, Qdrant, MinIO) — data sovereignty
- Primary LLM inference (vLLM on RTX 3090) — zero per-call cost
- All agent orchestration (n8n, Paperclip) — full control
- Visual AI (Frigate, YOLOv9) — camera privacy + latency
- Voice AI pipeline (Asterisk, Issabel) — SIP + low latency
- All FOSS business apps — no SaaS fees

#### Zone 2 — AWS Hybrid ($200 free credit)
```
Service       Role in AIOS                            Free Tier
──────────────────────────────────────────────────────────────────────
S3            Nightly backup — Postgres, Qdrant,       5GB free
              n8n exports, MinIO objects. 3-2-1 rule.
CloudFront    CDN for client portals + Metabase         1TB/mo free
              dashboards — faster global loading.
SES           ALL transactional emails — reports,       62,000 emails/mo free
              alerts, appointment confirmations.
EC2 t2.micro  Overflow compute — webhook processing     750 hrs/mo free
              when WS1 is under peak load.
Lambda        Serverless event routing — lightweight     1M requests/mo free
              webhook handlers, scheduled triggers.
Secrets Mgr   Backup for Vault credentials              30-day free trial
```
NOTE: Route 53 NOT used — Cloudflare handles all DNS.

#### Zone 3 — External Cloud APIs (paid per use, via Bifrost)
```
Service               Cost Model            Role
──────────────────────────────────────────────────────────────────────
Anthropic Claude API  Per token             Complex reasoning, long docs
OpenAI GPT-4o API     Per token             Vision, structured extraction
Google Gemini API     Per token             Multimodal fallback
Deepgram Nova 3       $0.0077/min           STT — Arabic/Urdu/English
ElevenLabs            $22/mo Creator        TTS — 29+ languages
Retell AI / Vapi      $0.07/min base        Voice agent platform
Meta WhatsApp API     $0.015/conversation   WhatsApp agents
Twilio                Per message/min       SMS + voice backup
```

### What Stays On-Prem vs What Goes to Cloud
```
STAYS ON-PREM (never leaves):
  Client data, agent memory, conversation history, documents
  RAG knowledge bases, business logic, workflow execution
  Camera feeds, voice recordings, all FOSS app data

GOES TO CLOUD (necessary only):
  LLM inference requests (text only — Bifrost strips PII if configured)
  STT audio (Deepgram — voice call audio)
  Encrypted backups (S3 — compressed + AES-256 encrypted)
  Email delivery (SES — reports and notifications)
  Static assets (CloudFront — dashboard CSS/JS)
```

---

## 6. CAPABILITIES LAYER

Capabilities sit between Core Infrastructure (Tiers 1–10) and Use Cases (top layer).
Each capability = combination of multiple tiers working together.
Built once. Reused across all industries. Powers unlimited use cases.

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
13  Multilingual AI               T3(Qwen 72B)+T5(Deepgram)           All UAE/Pakistan industries
14  Payment Processing            T6(n8n)+T8(JazzCash/Stripe)         Retail, Clinic, Academy
15  Email Automation              T1(IMAP)+T3+T6(n8n)                 Legal, Accounting, RE
16  Predictive Analytics          T7(data)+T9(scikit-learn+Metabase)   Retail, Pharmacy, Mfg
17  Attendance & Access Control   T4(Frigate face)+T8(ERPNext HR)      School, Factory, Office
18  Contract & E-Signing          T3+T6(n8n)+T8(Docuseal+Paperless)   Legal, Real estate, HR
19  Multi-Channel Routing         T1+T6(n8n routing)+T5               Call centre, Support
20  Agent Escalation              T6(n8n human-in-loop)+T1(WhatsApp)  All industries
```

---

## 7. USE CASES — TOP LAYER

Each use case = 1 n8n workflow running on the AIOS stack.

```
#   Use Case                 Channel              LLM                  App Integration
───────────────────────────────────────────────────────────────────────────────────────────
1   Smart Surveillance       Camera + WhatsApp    Frigate + LLaVA       Frigate + MQTT
2   Smart HR & Payroll       WhatsApp + Web       Mistral 7B            ERPNext HR
3   Smart Sales CRM          WhatsApp + Voice     OpenRouter            Twenty CRM + Calcom
4   AI Voice Receptionist    Voice (SIP)          Qwen 2.5              Asterisk + Dograh
```

---

## 8. DATA FLOWS

### WhatsApp — Use Case Request Lifecycle
```
End user sends WhatsApp message
→ Meta webhook → Cloudflare edge → OPNsense firewall
→ Traefik reverse proxy → CrowdSec WAF check
→ n8n workflow (use-case specific)
→ Bifrost guardrails (prompt injection scan)
→ Qdrant semantic search (platform knowledge base)
→ Langfuse (pulls versioned system prompt for this workflow)
→ Bifrost semantic cache check (cached? return immediately)
→ Bifrost routes to OpenRouter (cloud models)
→ Langfuse logs: prompt + response + cost + latency + tokens + model
→ OpenTelemetry traces full request path
→ n8n formats reply → WhatsApp API → end user
Total: under 3 seconds end-to-end
```

### Voice Call — Complete Lifecycle
```
Caller dials number
→ SIP trunk → Asterisk (voice zone) — call entry
→ Dograh (voice agent orchestration — replaces Retell AI/Vapi)
→ Whisper STT (local GPU)
→ n8n webhook → Bifrost → OpenRouter → LLM response
→ Chatterbox TTS (local GPU — replaces ElevenLabs)
→ Audio streamed back → Asterisk → caller
Full transcript logged in Langfuse.
```

### Visual AI — Camera Event Pipeline
```
IP camera RTSP stream → go2rtc → Frigate NVR
→ YOLOv9 on RTX 3090 (detects object: person/vehicle/face)
→ LLaVA generates description: "delivery driver at front door"
→ MQTT event published → n8n workflow fires
→ n8n → Bifrost → LLM → decides action
→ WhatsApp alert to owner + Supabase log + Grafana update
```

### Knowledge Document Ingestion
```
Admin uploads .md / PDF / SOP document
→ Supabase Storage receives file
→ n8n ingestion workflow triggers automatically
→ LlamaIndex chunks document into segments
→ nomic-embed-text generates vector embeddings (via Ollama)
→ Qdrant stores vectors in client's collection
Agent immediately has access to new knowledge. Zero restart required.
```

### Nightly Backup Pipeline
```
Cron trigger (2:00 AM daily) → n8n workflow
→ pg_dump Supabase → compressed → encrypted → S3
→ Qdrant snapshot → compressed → NAS + S3
→ n8n workflow export → NAS + S3
→ MinIO sync → S3
→ Success notification to WhatsApp
```

---

## 9. PROTOCOLS & STANDARDS

```
Protocol          Standard              Role
──────────────────────────────────────────────────────────────────────
MCP               Anthropic             Standardised tool connections for all agents
A2A               Google                Agent-to-agent communication
OpenTelemetry     CNCF                  Distributed tracing across all services
OAuth2 / OIDC     Industry standard     All auth flows via Keycloak
OpenAI API        De facto LLM standard Bifrost + vLLM both expose this
MQTT              IoT standard          Frigate event bus to n8n
SIP               Telecoms standard     Asterisk ↔ Issabel trunk
RTSP              Camera standard       All IP cameras to go2rtc
WireGuard         VPN standard          Cross-machine encrypted tunnel (via OPNsense)
NFS               Network storage       NAS mounted to both machines
```

---

---

## 11. DEVELOPMENT LAYER — COMPLETE STACK

### Architecture Type
AIOS is infrastructure development — not traditional app development.
You are building: Docker Compose configs, n8n workflow JSON, YAML configs,
Python scripts, Ansible playbooks, shell scripts.
You are NOT building: React apps, Express APIs, mobile apps.

This changes everything about your dev stack.

---

### The 7 Non-Negotiable Dev Tools

```
Tool              Role                                    Cannot Replace With
─────────────────────────────────────────────────────────────────────────────
1. Claude Code    Primary AI dev tool — SSH to WS1,       Nothing
   Desktop        writes + executes everything.
                  Reads CLAUDE.md for full context.
                  Writes Ansible, Docker Compose,
                  n8n workflows, Python scripts.
                  Executes on remote servers natively.

2. Git + GitHub   Version control for ALL configs,        Nothing
                  workflows, scripts, YAML files.
                  Every change tracked. Full history.
                  Rollback to any point in seconds.

3. ArgoCD         GitOps CD — watches GitHub 24/7,        Nothing
   (on WS1)       auto-deploys changes to Docker stack.
                  Push to GitHub → deployed automatically.
                  One-click rollback on failure.

4. Ansible        Server setup + disaster recovery.        Claude Code
                  Idempotent — run 10 times, same result.  (Claude Code needs you
                  Unattended — runs at 3am without you.    present. Ansible runs
                  Written by Claude Code, run by you.      unattended.)
                  Critical for: new server setup,
                  disaster recovery, team onboarding.

5. Hermes Agent   Autonomous 24/7 server ops.             Nothing
   (on WS1)       Monitors disk, restarts crashed
                  services, alerts via WhatsApp.
                  No human needed — runs by itself.

6. OpenClaw       Your personal AI assistant.             Nothing
   (on laptop)    Manages your inbox, calendar, tasks
                  via WhatsApp/Telegram. Always on.

7. GitHub Actions CI validation on every git push.        Nothing
   Runner         Validates YAML syntax, runs pytest,
   (on WS1)       Trivy security scan — before ArgoCD
                  deploys anything to production.
```

---

### Claude Code — How It Works in Your AIOS

```
WHAT CLAUDE CODE DOES:
  Connects to WS1 via Desktop SSH (native tools — full experience)
  Reads /aios/ directory — knows your entire project
  Reads CLAUDE.md — knows your architecture rules automatically
  Reads PROJECT.md — knows every decision ever made

  Writes:
    docker-compose-aios.yml changes
    docker-compose-apps.yml changes
    Ansible playbooks for server setup
    Python scripts (backup.py, health-check.py)
    n8n workflow JSON templates
    GitHub Actions CI YAML
    Bifrost routing configs
    Traefik routing rules
    Shell scripts

  Executes on WS1:
    docker-compose up -d
    ansible-playbook setup-ws1.yml
    python3 health-check.py
    systemctl restart service
    Fixes errors as they appear — reads output, retries

CLAUDE CODE SSH MODES:
  Desktop SSH (preferred):
    Same as working locally — full native Read/Write/Edit tools
    Full tool suite — best experience for AIOS development

  CLI SSH (fallback):
    Uses bash one-off commands
    Works but limited — file ops via cat heredocs
    Use when Desktop not available
```

---

### Ansible — Where It Fits

```
ANSIBLE PLAYBOOKS (written by Claude Code, run by you):
  /aios/ansible/
  ├── inventory.yml              # WS1 + Inference Server IPs
  ├── setup-ws1.yml              # Full WS1 first-time setup
  │   Sets up: Ubuntu packages, Docker, KVM,
  │            OPNsense VM, Issabel VM, WireGuard,
  │            directory structure, pull Docker images
  ├── setup-inference.yml        # Full Inference Server setup
  │   Sets up: Ubuntu, Docker, NVIDIA drivers, CUDA,
  │            vLLM, Frigate, NAS mount
  ├── update-configs.yml         # Push config changes manually
  └── /roles/
      ├── docker/                # Install Docker role
      ├── nvidia/                # Install NVIDIA drivers + CUDA
      ├── kvm/                   # Set up KVM + VMs
      ├── wireguard/             # Configure WireGuard tunnel
      └── aios-directories/      # Create /aios/ folder structure

WHEN TO RUN ANSIBLE:
  First time:    ansible-playbook setup-ws1.yml      (server setup)
  Disaster:      WS1 dies → new machine → run playbook → identical
  New server:    Scale to 3rd machine → run playbook → configured
  New engineer:  They run playbook → their env matches yours exactly
```

---

### Your Dev PC / Laptop — What to Install

```
INSTALL:
  VS Code                     code.visualstudio.com
  VS Code Remote SSH plugin   edit files on WS1 from laptop
  Claude Code Desktop         claude.ai/code
  Git                         git-scm.com
  Python 3                    python.org
  Bruno (API testing)         usebruno.com — free, open source
  
CONNECT TO:
  WS1 via Claude Code Desktop SSH → primary interface
  WS1 via VS Code Remote SSH      → backup editor
  All WS1 dashboards via browser  → n8n, Grafana, Langfuse etc.

NOT NEEDED ON LAPTOP:
  Docker daemon (everything runs on WS1)
  Node.js server
  Database
  Any AIOS service
```

---

### Git Branching Strategy

```
main branch:     production — ArgoCD deploys from here
dev branch:      staging — test here before promoting to main
feature/* :      new capabilities, new configs

Workflow:
  Create feature branch → Claude Code builds on WS1
  Push feature → GitHub Actions CI validates
  PR to dev → team reviews
  Test on dev environment
  PR from dev to main → ArgoCD deploys to production
  If issue → ArgoCD one-click rollback
```

---

### Directory Structure — Complete

```
/aios/
├── CLAUDE.md                        # Claude Code instructions (AUTO-READ)
├── docker-compose-aios.yml          # AI core services (Docker Layer B)
├── docker-compose-apps.yml          # FOSS business apps (Docker Layer A)
├── .env.aios                        # AI core env vars (from Vault)
├── .env.apps                        # Apps env vars (from Vault)
├── /ansible/
│   ├── inventory.yml                # Server IPs
│   ├── setup-ws1.yml                # WS1 full setup playbook
│   ├── setup-inference.yml          # Inference Server setup playbook
│   └── /roles/                      # Ansible roles
├── /configs/
│   ├── /traefik/                    # Traefik routing rules
│   ├── /crowdsec/                   # CrowdSec WAF rules
│   ├── /keycloak/                   # Keycloak realm exports
│   ├── /bifrost/                    # Bifrost routing + budget config
│   ├── /opnsense/                   # OPNsense firewall backup
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
│   └── disaster-recovery.py         # Full system restore script
└── /docs/
    ├── PROJECT.md                   # Master reference (this file)
    ├── CLAUDE.md                    # Claude Code project instructions
    └── /capabilities/               # One .md doc per capability
```

---

### Environment Variables — Critical

```bash
# Bifrost AI Gateway
BIFROST_URL=http://10.40.0.10:4000
BIFROST_ADMIN_KEY=<from Vault>

# vLLM Inference Server (via WireGuard)
VLLM_URL=http://10.70.0.2:8000
VLLM_API_KEY=<from Vault>

# Cloud LLMs (via Bifrost — do NOT call directly)
ANTHROPIC_API_KEY=<from Vault>
OPENAI_API_KEY=<from Vault>
GOOGLE_API_KEY=<from Vault>

# Voice
DEEPGRAM_API_KEY=<from Vault>
ELEVENLABS_API_KEY=<from Vault>
RETELL_API_KEY=<from Vault>

# WhatsApp
WHATSAPP_TOKEN=<from Vault>
WHATSAPP_PHONE_ID=<from Vault>

# Data
SUPABASE_URL=http://10.30.0.10:8000
SUPABASE_KEY=<from Vault>
QDRANT_URL=http://10.30.0.20:6333
REDIS_URL=redis://10.30.0.30:6379
MINIO_URL=http://10.30.0.40:9000
MINIO_KEY=<from Vault>

# Monitoring
LANGFUSE_URL=http://10.60.0.10:3000
LANGFUSE_KEY=<from Vault>
GRAFANA_URL=http://10.60.0.30:3000
```

---

### Critical Development Rules

```
1. NEVER call any LLM API directly.
   ALL calls go through Bifrost (http://10.40.0.10:4000).
   Bifrost = cost tracking, caching, failover, client billing.

2. NEVER hardcode API keys anywhere.
   All secrets live in HashiCorp Vault.
   Injected at container runtime via .env files pulled from Vault.

3. NEVER expose Inference Server (192.168.1.20) to internet.
   Internal only. WireGuard tunnel (10.70.0.2) only.

4. ALWAYS log every LLM call to Langfuse for cost tracking.

5. Data Zone (10.30.0.0/24) has internal:true.
   Databases CANNOT reach internet. Do not change this ever.

6. ALWAYS commit to Git before applying any change to production.
   No direct edits on WS1 without committing first.
   Git is the single source of truth.
```

---

### Adding a New Use Case

```
1. Build the workflow in n8n
2. HTTP POST → Bifrost → OpenRouter for inference
3. Log to Langfuse for observability + cost tracking
4. Test end-to-end with real data
5. Run on the AIOS stack
6. git commit + push
```

---

### Environment Variables — Critical
```bash
# Bifrost AI Gateway
BIFROST_URL=http://10.40.0.10:4000
BIFROST_ADMIN_KEY=<from Vault>

# vLLM Inference Server (via WireGuard)
VLLM_URL=http://10.70.0.2:8000
VLLM_API_KEY=<from Vault>

# Cloud LLMs (via Bifrost — do NOT call directly)
ANTHROPIC_API_KEY=<from Vault>
OPENAI_API_KEY=<from Vault>
GOOGLE_API_KEY=<from Vault>

# Voice
DEEPGRAM_API_KEY=<from Vault>
ELEVENLABS_API_KEY=<from Vault>
RETELL_API_KEY=<from Vault>

# WhatsApp
WHATSAPP_TOKEN=<from Vault>
WHATSAPP_PHONE_ID=<from Vault>

# Data
SUPABASE_URL=http://10.30.0.10:8000
SUPABASE_KEY=<from Vault>
QDRANT_URL=http://10.30.0.20:6333
REDIS_URL=redis://10.30.0.30:6379

# Monitoring
LANGFUSE_URL=http://10.60.0.10:3000
LANGFUSE_KEY=<from Vault>
```

### Critical Rules for Development
```
1. NEVER call Claude API, GPT-4o, or any LLM directly.
   Always route through Bifrost (http://10.40.0.10:4000).

2. NEVER hardcode API keys.
   All secrets are in HashiCorp Vault. Injected at container runtime.

3. NEVER expose Inference Server (192.168.1.20) to internet.
   It is internal only. Access via WireGuard tunnel (10.70.0.2) only.

4. ALWAYS log every LLM call to Langfuse for cost tracking.

5. Data Zone (10.30.0.0/24) has internal:true in Docker.
   Databases cannot reach internet. Do not change this.
```

### Adding a New Use Case (workflow)
```
1. Build and test in Flowise or Dify first (rapid prototype)
2. Translate to n8n workflow (production)
3. Test with Ollama dev instance on WS1 (zero cost)
4. Validate with Langfuse (check prompt quality + cost)
5. Run on the AIOS stack
```

---

## 12. PHASES & SCALE PLAN

### Phase 1 — Lab (Now, 45 days)
```
Infrastructure:  2 machines set up, all Docker stacks running
Goal:            5 working prototypes — clinic, HR, real estate, retail, accounting
Team:            Senior AI Engineer + Voice Dev + Full-Stack Dev + QA/DevOps
Kubernetes:      NO — Docker Compose only
```

### Phase 2 — First Clients (Month 3–6)
```
Action:          Start selling Lahore SMBs
Clients:         3 → 18 clients
Revenue:         PKR 197K → PKR 582K/month
Kubernetes:      NO — same Docker stack
UAE prep:        Build bilingual Arabic/English agents
```

### Phase 3 — Scale (Month 7+)
```
Break-even:      Month 7 (25 clients, PKR 742K revenue)
Month 12 target: 60 clients, PKR 940K MRR
UAE entry:       Month 9–12 (government mandate = forced demand)
US/Canada:       Month 12–18 (white-label partnerships)
Kubernetes:      Add K3s ONLY when 100+ clients or auto-scaling needed
HA:              Add 3rd physical machine for true failover
```

### What This Architecture Does NOT Have Yet (honest)
```
Feature               Status        When to add
──────────────────────────────────────────────────────────────────
True HA               Not yet       Phase 3 — needs 3rd machine
Auto-scaling          Not yet       Phase 3 — K3s
Multi-region          Not yet       Phase 3 — UAE data centre
Postgres replica      Partial       Phase 2 — add replica node
Full SOC2             Partial       Phase 2 — audit logs present
AWS-equivalent        Not yet       Phase 3 — current is professional
                                    self-hosted production, not cloud-native HA
```

---

## 13. MARKET CONTEXT

### Target Markets — Sequenced
```
Phase       Market                  Timing        Strategy
──────────────────────────────────────────────────────────────────
Phase 1     Pakistan (Lahore)       Now           Direct sales. Clinics, HR, real estate,
                                                  pharmacies, academies.
                                                  PKR 35–75K setup + PKR 12–22K MRR.
Phase 2A    UAE (Dubai/Abu Dhabi)   Month 9–12    Government mandate = forced demand.
                                                  Bilingual Arabic/English agents.
                                                  3–4× Pakistan pricing. $1,500 setup + $450/mo.
Phase 2B    US & Canada             Month 12–18   White-label partnerships with local agencies.
                                                  Supply them with vertical SMB products.
                                                  No direct sales team needed.
```

### 2026 Market Reality
```
- 64% enterprises using AI (NVIDIA 2026)
- 57% SMBs investing in AI — up from 36% in 2023
- 7% SMBs running production AI agents vs 34% enterprises
- 93 out of 100 SMBs have NO AI agents — this is the market
- $52.62B AI agent market by 2030 at 46.3% CAGR
- UAE: 50% of federal services mandated to agentic AI (April 23, 2026)
- Gartner: Only ~130 of thousands of AI agent vendors are real — rest are agent-washing
```

---

## 14. QUICK REFERENCE — ALL TOOLS SUMMARY

### By Machine
```
WS1 KVM VMs:          OPNsense, Issabel
WS1 Docker Layer A:   Odoo, ERPNext, Twenty CRM, SuiteCRM, Calcom,
                      Paperless-ngx, Docuseal, Planka, Rocket.Chat,
                      Frappe LMS, GnuCash, Metabase
WS1 Docker Layer B:   Traefik, CrowdSec, Keycloak, HashiCorp Vault,
                      Bifrost, LiteLLM(dev), Ollama(dev), MQTT,
                      Asterisk, n8n+workers, Flowise, Dify, Paperclip,
                      Hermes, Langfuse, Qdrant, Supabase, Redis,
                      MinIO, Open WebUI, Grafana, Prometheus, Loki,
                      Portainer, Dashy, Uptime Kuma, Dozzle,
                      ArgoCD, Watchtower, Trivy,
                      GitHub Actions Runner, SonarQube (Phase 2)
WS1 Installed:        Claude Code (Desktop + CLI), OpenClaw, Ansible
Dev PC/Laptop:        VS Code + Remote SSH, Bruno (API testing),
                      Git, Python 3, Claude Code Desktop
Inference Server:     vLLM, Frigate, LLaVA, YOLOv9, go2rtc,
                      nvidia-smi exporter
Cloud APIs:           Claude 4 Sonnet, GPT-4o, Gemini, Deepgram,
                      ElevenLabs, Retell AI, WhatsApp API, Twilio
AWS Hybrid:           S3, CloudFront, SES, EC2 t2.micro, Lambda,
                      Secrets Manager
```

### By Type
```
FOSS (self-hosted):   n8n, Flowise, Dify, Qdrant, Supabase, Redis,
                      MinIO, Langfuse, Grafana, Prometheus, Loki,
                      Traefik, CrowdSec, Keycloak, Vault, Portainer,
                      Dashy, Uptime Kuma, Dozzle, ArgoCD, Watchtower,
                      Trivy, Paperclip, Hermes, OpenClaw, Frigate,
                      go2rtc, Asterisk, Issabel, OPNsense, Odoo,
                      ERPNext, Twenty CRM, SuiteCRM, Calcom,
                      Paperless-ngx, Docuseal, Planka, Rocket.Chat,
                      Frappe LMS, GnuCash, Metabase, vLLM, Ollama,
                      LiteLLM, CrewAI, LangGraph, Open WebUI
Paid subscriptions:   Claude Code Max, ElevenLabs, Retell AI/Vapi,
                      Deepgram, WhatsApp Business API, Cloudflare Pro
Cloud APIs (usage):   Anthropic Claude, OpenAI GPT-4o, Google Gemini,
                      Twilio
AWS (hybrid):         S3, CloudFront, SES, EC2, Lambda
Free tiers:           Cloudflare free, AWS free tier, Deepgram $200 credit,
                      AWS $200 credit
```

---

*AIOS PROJECT.md — Complete Reference*
*Version: Final · May 2026 · Lahore AI Lab*
*All decisions locked. Do not modify architecture without updating this document.*

---

## 15. USE-CASE DIRECT WORKFLOW MODEL

MVP uses standalone self-contained n8n workflows — no capabilities layer.

Each use case is a single n8n workflow with all logic inline:
```
n8n/workflows/
├── 01-surveillance.json        # Frigate → GPU vision → n8n → WhatsApp
├── 02-hr-payroll.json          # Face recognition + GPS + salary
├── 03-sales-crm.json           # Leads → WhatsApp CRM → pipeline
└── 04-voice-receptionist.json  # Asterisk → Dograh → STT → LLM → TTS
```

Each workflow:
- Has its own Set Variables node (model, prompt key, collection ID)
- Calls Bifrost → OpenRouter for LLM inference
- Logs to Langfuse
- Is built, tested, and deployed independently
  YES → Node 5
  NO  → Node 8 (suggest alternatives)

NODE 5: Call Bifrost → {{model}}
  System prompt: pulled from Langfuse {{prompt_key}}
  Task: generate confirmation message in patient language

NODE 6: Book in ERPNext
  POST {{erp_url}}/api/resource/Patient Appointment
  Returns: {appointment_id: "APT-2024-1234"}

NODE 7: Book in Google Calendar
  Creates event in {{calendar_id}}

OUTPUT:
  {booked:true, appointment_id:"APT-1234", fee:"PKR 1500", confirmation_urdu:"..."}

NODE 8 (NO path): Query ERPNext for alternative slots
NODE 9 (NO path): Generate alternatives message via Bifrost
OUTPUT (NO):
  {booked:false, alternatives:["16:00","09:00+1","11:00+1"], message_urdu:"..."}
```

---


---

---
│ 2. Upload docs → http://qdrant/clinic-abc      │
│ 3. Test WhatsApp → +923001234567               │
│ 4. Test voice   → +92111234567                 │
│ ─────────────────────────────────────────────── │
│ Automation time:   11 minutes                  │
│ Manual time:       ~45 minutes                 │
│ Total to live:     ~1 hour                     │
└─────────────────────────────────────────────────┘
```

---

## 17. PHASE 1 — EXACT DELIVERABLES

### Week-by-Week Build Plan

```
WEEK 1: Infrastructure setup
  Server configured — Docker, GPU, 8 networks
  Docker Layer A (FOSS) + Layer B (AI core) deployed
  All services accessible via Dashy
  All 13 public endpoints verified 200

WEEK 2: Use case — CRM (#3)
  Build 03-sales-crm.json n8n workflow
  Wire: webhook → OpenRouter → PostgreSQL → Langfuse
  Test end-to-end via webhook

WEEK 3: Use case — Voice (#4)
  Wire Asterisk → Dograh → Chatterbox → OpenRouter
  Test call pipeline end-to-end
  Build 04-voice-receptionist.json n8n workflow

WEEK 4: Use case — HR (#2)
  Build 02-hr-payroll.json n8n workflow
  Test GPU vision (face recognition via Ollama/LLaVA)

WEEK 5-6: Use case — Surveillance (#1)
  Connect IP cameras → Frigate → GPU detection
  Build 01-surveillance.json n8n workflow
  Wire MQTT → n8n → WhatsApp alerts
  Full integration test all 4 use cases
```

### Definition of Done for Each Use Case

```
✅ n8n workflow in /aios/n8n/workflows/{number}-{name}.json
✅ HTTP POST → Bifrost → OpenRouter for inference
✅ All LLM calls logged to Langfuse
✅ Tested end-to-end with real data
✅ Functional frontend/dashboard built
```

---

*Updated: June 2026 — AIOS PROJECT v2*
