# AIOS — AI Operating System
## Complete Project Reference for Claude Code
### Lahore AI Lab · May 2026 · FINAL LOCKED

---

## 1. PROJECT OVERVIEW

### What This Is
AIOS (AI Operating System) is a production-grade, self-hosted, hybrid AI platform built in a physical lab in Lahore, Pakistan. It is designed to:

1. **Serve as an AI R&D lab** — build, test, and prototype all AI use cases
2. **Serve as a production template** — the exact same architecture is cloned and deployed for each SMB client
3. **Power a commercial AI agency** — selling AI Digital Employees to SMBs across Pakistan, UAE, and USA

### Business Context
- **Founder:** Senior IT infrastructure specialist, 20+ years experience, documented government-scale AI transformation (38,000-school SED deployment)
- **Business model:** Sell AI Digital Employees (voice agents, WhatsApp agents, workflow automation) to SMBs
- **Target markets:** Pakistan (Lahore) → UAE (Dubai/Abu Dhabi) → USA/Canada (white-label)
- **Revenue model:** PKR 35–75K setup fee + PKR 12–22K monthly recurring per client
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

### Multi-Tenant Client Isolation
Each SMB client gets completely isolated:
```
Keycloak:   Separate tenant — users cannot see other clients
Qdrant:     Separate collection — agent only searches their data
Supabase:   Separate schema + row-level security
Bifrost:    Separate virtual key with monthly budget limit
n8n:        Separate workflow tagged to their tenant
Langfuse:   Separate prompt project tagged to client
Paperclip:  Separate company with full data isolation
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
Keycloak            WS1 Docker B    SSO, multi-tenant isolation, RBAC, OAuth2/OIDC
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

Each use case = 1 n8n workflow + 1 Qdrant collection + 1 Keycloak tenant +
1 Bifrost virtual key + 1 Langfuse prompt + 1 Paperclip company agent.

New client onboarding = 2–3 hours. Zero new infrastructure.

```
#   Use Case                  Channel              LLM                  Replaces              App
─────────────────────────────────────────────────────────────────────────────────────────────────────
1   Clinic AI Receptionist    Voice + WhatsApp     Llama 70B + Qwen     Manual receptionist   ERPNext Hospital
2   HR AI Assistant           WhatsApp + Web       Mistral 7B           HR admin routine      ERPNext HR
3   Real Estate Lead Agent    WhatsApp + Voice     Claude 4 Sonnet      Manual follow-up      Twenty CRM + Calcom
4   Retail Inventory AI       Web + WhatsApp       Mistral 7B + Frigate Manual stock mgmt     ERPNext POS
5   Accounting AI             WhatsApp + Web       GPT-4o + LLaVA       Manual data entry     Paperless-ngx + GnuCash
6   Pharmacy AI               WhatsApp + Voice     Llama 70B + Frigate  Manual ordering       ERPNext POS
7   Hotel Concierge AI        Voice + WhatsApp     Claude 4 + ElevenLabs Front desk routine   ERPNext Hotel
8   Call Centre AI            Voice (Asterisk)     Qwen 72B Urdu/Arabic Human agents          Issabel call centre
9   Legal AI                  Web + Email          Claude 4 long ctx    Manual doc review     Paperless-ngx + Docuseal
10  Academy AI                WhatsApp + Web       Mistral + Qwen       Admin staff           Frappe LMS + ERPNext Edu
11  Security AI               Camera feeds         Frigate + LLaVA      Manual monitoring     Frigate pipeline
12  Logistics AI              WhatsApp + API       Mistral 7B           Manual tracking       ERPNext + n8n
```

---

## 8. DATA FLOWS

### WhatsApp Agent — Complete Request Lifecycle
```
Client sends WhatsApp message
→ Meta webhook → Cloudflare edge → OPNsense firewall
→ Traefik reverse proxy → CrowdSec WAF check
→ Keycloak auth (tenant validated)
→ n8n workflow (client-specific, tagged to tenant)
→ Bifrost guardrails (prompt injection scan)
→ Qdrant semantic search (client knowledge base RAG)
→ Langfuse (pulls versioned system prompt for this client)
→ Bifrost semantic cache check (cached? return immediately)
→ Bifrost routes to vLLM (local) OR Claude API (cloud)
→ Langfuse logs: prompt + response + cost + latency + tokens + model
→ OpenTelemetry traces full request path
→ n8n formats reply → WhatsApp API → client receives answer
Total: under 3 seconds end-to-end
```

### Voice Call — Complete Lifecycle
```
Caller dials number
→ Issabel (KVM VM — GUI + dashboard + recordings)
→ SIP trunk → Asterisk (WS1 Docker) — AI pipeline entry
→ Retell AI / Vapi (conversation orchestration)
→ Deepgram Nova 3 STT (Arabic/Urdu/English real-time)
→ n8n webhook → same pipeline as WhatsApp above
→ Bifrost → vLLM / Claude → response text
→ ElevenLabs TTS (natural voice synthesis)
→ Audio streamed back → Asterisk → Issabel → caller
Call recorded in Asterisk. Full transcript logged in Langfuse.
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

## 10. CLIENT DEPLOYMENT GUIDE

### What Goes to Client vs What Stays in Lab

#### REMOVED for client deployment (lab-only tools):
```
- Claude Code (your dev tool)
- Hermes Agent (your DevOps agent)
- OpenClaw (your personal assistant) — client gets their OWN fresh instance
- Paperclip internal company — client gets their OWN company
- LiteLLM dev instance
- Ollama dev instance
- ArgoCD (your CI/CD pipeline)
- Flowise/Dify (optional — only if client wants to build agents)
```

#### KEPT for client deployment (everything else):
All Tiers 1–10, FOSS apps relevant to their industry, Paperclip with their company, Metabase dashboards, all monitoring tools, Grafana client organisation.

#### CONFIGURED for client:
```
Step  Action                                        Tool              Time
─────────────────────────────────────────────────────────────────────────
1     Create new tenant in Keycloak                 Keycloak admin    5 min
2     Create Qdrant collection for client           Qdrant API        2 min
3     Create Supabase schema + RLS policies         Supabase dash     5 min
4     Create Bifrost virtual key + budget           Bifrost admin     2 min
5     Create Paperclip company for client           Paperclip dash    5 min
6     Upload client knowledge docs → Qdrant         n8n ingestion     30 min
7     Configure agent system prompt in Langfuse     Langfuse UI       20 min
8     Clone n8n workflow template → tag to client   n8n dashboard     30 min
9     Connect WhatsApp number or voice SIP          WA API + Retell   15 min
10    Test end-to-end → live demo → sign-off        Manual test       30 min
─────────────────────────────────────────────────────────────────────────
      Total: client fully live                                     2–3 hours
```

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
    Python scripts (new-client.py, backup.py)
    n8n workflow JSON templates
    GitHub Actions CI YAML
    Bifrost routing configs
    Traefik routing rules
    Shell scripts

  Executes on WS1:
    docker-compose up -d
    ansible-playbook setup-ws1.yml
    python3 new-client.py --client-id clinic-abc
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
│   ├── new-client.py                # Client onboarding automation
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

3. ALWAYS tag n8n workflows with client_id variable.
   Cross-client data leakage is a critical security failure.

4. ALWAYS enforce Supabase RLS on every table.
   Schema per client + Row Level Security = double isolation.
   Never rely on application filtering alone.

5. NEVER expose Inference Server (192.168.1.20) to internet.
   Internal only. WireGuard tunnel (10.70.0.2) only.

6. ALWAYS log every LLM call to Langfuse.
   This is how per-client billing is calculated.

7. Data Zone (10.30.0.0/24) has internal:true.
   Databases CANNOT reach internet. Do not change this ever.

8. ALL new client resources created via new-client.py only.
   Never create Keycloak/Qdrant/Supabase/Bifrost resources manually.
   Manual = inconsistent = mess at scale.

9. ALL capability sub-workflows must have zero client hardcoding.
   All client-specific data passed as variables only.

10. ALWAYS commit to Git before applying any change to production.
    No direct edits on WS1 without committing first.
    Git is the single source of truth.
```

---

### Adding a New Capability Template

```
1. Build prototype in Flowise or Dify (visual, fast)
2. Export logic to n8n sub-workflow JSON
3. Replace ALL client-specific values with variables
4. Test with at least 2 different dummy client configs
5. Validate in Langfuse — check prompt quality + cost
6. Save to: /aios/n8n/workflow-templates/capabilities/cap-[name].json
7. Write doc: /aios/docs/capabilities/cap-[name].md
8. Update new-client.py to support this capability
9. git commit + push → ArgoCD deploys to n8n
```

---

### Adding a New Use Case Template

```
1. Identify which capabilities it chains
2. Build main workflow in n8n — chain capability sub-workflows
3. All client variables defined in Node 2 (Set Variables)
4. Intent routing (IF/SWITCH) routes to correct capabilities
5. Final nodes: Supabase log + Langfuse log
6. Test with dummy client data end-to-end
7. Save to: /aios/n8n/workflow-templates/use-case-templates/
8. git commit + push
```

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
   Bifrost handles cost tracking, caching, fallover, and client billing.

2. NEVER hardcode API keys.
   All secrets are in HashiCorp Vault. Injected at container runtime.

3. ALWAYS tag n8n workflows with client tenant ID.
   Prevents cross-client data leakage.

4. ALWAYS use Supabase Row Level Security.
   Every client has their own schema. RLS is enforced.

5. NEVER expose Inference Server (192.168.1.20) to internet.
   It is internal only. Access via WireGuard tunnel (10.70.0.2) only.

6. ALWAYS log every LLM call to Langfuse.
   This is how we track per-client costs for billing.

7. Data Zone (10.30.0.0/24) has internal:true in Docker.
   Databases cannot reach internet. Do not change this.

8. Each new client needs entries in:
   Keycloak + Qdrant + Supabase + Bifrost + Langfuse + Paperclip + n8n.
   Use the new-client.py script to automate this.
```

### Adding a New Use Case (workflow)
```
1. Build and test in Flowise or Dify first (rapid prototype)
2. Translate to n8n workflow (production)
3. Test with Ollama dev instance on WS1 (zero cost)
4. Validate with Langfuse (check prompt quality + cost)
5. Save as template in /n8n/workflows/client-templates/
6. Document in /docs/ with capability mapping
7. Update new-client.py to include new use case option
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

## 15. CAPABILITIES — TECHNICAL DEFINITION & IMPLEMENTATION

### What a Capability Is — Technically

A capability is a **reusable n8n sub-workflow template** with variable inputs and no client-specific hardcoding. It does ONE specific job. It knows nothing about which client is calling it. All client-specific data is passed as variables from the main workflow.

**Capability is NOT:**
- A Docker container
- A separate server or service
- A Tier in the architecture
- A technical component you install

**Capability IS:**
- An n8n sub-workflow JSON file stored in /workflow-templates/capabilities/
- Called by main workflows using n8n "Execute Sub-Workflow" node
- Reused across unlimited clients without modification
- A building block — not a finished product

---

### Three Core Concepts — Clearly Separated

```
CAPABILITY  = Reusable sub-workflow template (the building block)
              Does ONE job. Has variables. No client context.
              Example: cap-appointment-booking.json

MAIN WORKFLOW = Client-specific orchestrator (the manager)
              Receives input. Routes. Chains capabilities together.
              Has client variables filled in.
              Example: clinic-abc-main.json

AGENT       = The AI entity with personality, memory, and goal
              Paperclip entry + Langfuse prompt + n8n workflow
              Example: "Sarah — Clinic ABC Receptionist"
```

**The analogy:**
```
Capability    = Specialist staff member (does one job perfectly)
Main workflow = Manager (receives requests, delegates to specialists)
Agent         = The persona/identity of that manager
```

**Key rule:**
```
Main workflows USE capabilities
Capabilities do NOT know about main workflows
Capabilities do NOT know about clients
```

---

### n8n Folder Structure — Complete

```
n8n/
│
├── /workflow-templates/
│   │
│   ├── /capabilities/              ← 20 CAPABILITY SUB-WORKFLOWS
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
│   └── /use-case-templates/        ← 12 MAIN WORKFLOW TEMPLATES
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
└── /clients/                       ← DEPLOYED CLIENT WORKFLOWS
    ├── /clinic-abc/
    │   └── clinic-abc-main.json    ← cloned from template-clinic-main.json
    ├── /pharmacy-xyz/
    │   └── pharmacy-xyz-main.json  ← cloned from template-pharmacy-main.json
    └── /[client-id]/
        └── [client-id]-main.json
```

---

### What Is Inside a Capability Sub-Workflow

Every capability sub-workflow has this structure:

```
INPUT:  variables passed from main workflow
        {
          client_id:      "clinic-abc"
          collection_id:  "clinic-abc-knowledge"
          prompt_key:     "clinic-abc-receptionist-v1"
          model:          "qwen-2.5-72b"
          [capability-specific variables]
        }

NODES:  logic steps using Tier 3-8 tools
        (Bifrost, Qdrant, Supabase, ERPNext, Calcom etc.)

OUTPUT: result returned to main workflow
        {
          success: true/false
          [capability-specific result data]
        }
```

**KEY RULE: No client name, no client data hardcoded inside capability.**
Everything comes in as a variable. This is what makes it reusable.

---

### What Is Inside a Main Workflow

Every main workflow (client-specific) has this structure:

```
[NODE 1] Trigger
  Type: Webhook (WhatsApp) or SIP (Voice) or Cron (scheduled)

[NODE 2] Set Client Variables
  client_id      = "clinic-abc"           ← FILLED AT CLONE TIME
  collection_id  = "clinic-abc-knowledge" ← FILLED AT CLONE TIME
  prompt_key     = "clinic-abc-v1"        ← FILLED AT CLONE TIME
  model          = "qwen-2.5-72b"         ← FILLED AT CLONE TIME
  erp_url        = "http://..."           ← FILLED AT CLONE TIME

[NODE 3-N] Execute Sub-Workflow (capability calls — chained)
  Call: cap-multilingual         → detect language, translate
  Call: cap-intent-detection     → understand what user wants
  Call: cap-[relevant]           → do the actual work
  Call: cap-proactive-notifications → send response to user

[FINAL NODE] Log
  Supabase: save conversation
  Langfuse:  save LLM cost + tokens
```

---

### Chaining — How It Works in n8n

Chaining = main workflow calls capability sub-workflows in sequence using **Execute Sub-Workflow** node. Output of one becomes input of next.

```
EXAMPLE: Clinic ABC — Patient books appointment via WhatsApp

Patient sends: "Dr Ahmed se appointment chahiye kal 3 baje" (Urdu)

[MAIN: clinic-abc-main]
        ↓
[Execute Sub-Workflow: cap-multilingual]
  Input:  raw Urdu message
  Output: {language:"urdu", translated:"I want appointment with Dr Ahmed tomorrow 3pm"}
        ↓
[Execute Sub-Workflow: cap-intent-detection]
  Input:  translated message
  Output: {intent:"appointment_booking", entities:{doctor:"Dr Ahmed", date:"tomorrow", time:"3pm"}}
        ↓
[IF/SWITCH — route by intent]
  appointment_booking → Execute Sub-Workflow: cap-appointment-booking
  faq                 → Execute Sub-Workflow: cap-faq-support
  complaint           → Execute Sub-Workflow: cap-agent-escalation
        ↓
[Execute Sub-Workflow: cap-appointment-booking]
  Input:  doctor + date + time + client variables
  Does:   checks ERPNext availability
          queries Qdrant for clinic rules
          calls Bifrost → Qwen 72B
          books in ERPNext
          books in Google Calendar
  Output: {booked:true, appointment_id:"APT-1234", confirmation_urdu:"آپ کی اپائنٹمنٹ..."}
        ↓
[Execute Sub-Workflow: cap-proactive-notifications]
  Input:  confirmation message + patient phone + language
  Does:   sends WhatsApp confirmation in Urdu
  Output: {sent:true, message_id:"wamid.xxx"}
        ↓
[Supabase log + Langfuse log]
  Saves: full conversation, appointment_id, cost, timestamp
```

---

### Full Technical Example — cap-appointment-booking.json

```
INPUT VARIABLES:
  doctor_name, requested_date, requested_time, patient_phone
  client_id, collection_id, calendar_id, erp_url
  prompt_key, model

NODE 1: Resolve date/time
  "tomorrow 3pm" → "2024-01-15 15:00:00"

NODE 2: Query ERPNext — check doctor schedule
  GET {{erp_url}}/api/resource/Doctor/{{doctor_name}}/schedule
  Returns: available slots, booked slots

NODE 3: Query Qdrant RAG — check clinic rules
  Search {{collection_id}} for "{{doctor_name}} rules fee"
  Returns: "Dr Ahmed works Mon-Sat 9am-9pm. Fee PKR 1500."

NODE 4: IF slot available?
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

### How Adding a Module Works for New Client

**Adding capability to existing client = 30–60 minutes:**

```
Step 1: Clone capability template in n8n         (2 min)
Step 2: Fill client variables                    (10 min)
        collection_id, prompt_key, model,
        erp_url, calendar_id etc.
Step 3: Add Execute Sub-Workflow node to         (5 min)
        client's main workflow
Step 4: Connect to existing chain                (5 min)
Step 5: Test                                     (20 min)
Total:  ~45 minutes
```

**Adding NEW client with existing templates = 1 hour total:**

```
Automated (new-client.py script):    10–12 minutes
  Keycloak tenant created
  Qdrant collection created
  Supabase schema + RLS created
  Bifrost virtual key + budget created
  Paperclip company + agent created
  Langfuse project created
  n8n main workflow cloned from industry template
  All variables filled automatically
  Selected capabilities enabled
  Unselected capabilities disabled

Manual (human required):             45–50 minutes
  Fill system prompt in Langfuse     (15-20 min)
  Upload client knowledge docs       (20-30 min)
  Run end-to-end test                (15 min)

Total: ~1 hour vs 2-3 hours manual
```

---

## 16. NEW CLIENT ONBOARDING — FORM FIELDS

When onboarding a new client via new-client.py script, these are the exact inputs required:

```
BASIC INFO
──────────────────────────────────────────────
client_id          = "clinic-abc"          # unique slug, no spaces, lowercase
client_name        = "Clinic ABC"          # display name
industry           = "clinic"              # dropdown: clinic/hr/realestate/retail/
                                           # accounting/pharmacy/hotel/callcentre/
                                           # legal/academy/security/logistics
contact_name       = "Dr. Ahmed"
contact_phone      = "+923001234567"
contact_email      = "ahmed@clinic.com"

LANGUAGE & REGION
──────────────────────────────────────────────
primary_language   = "urdu"               # urdu / arabic / english
secondary_language = "english"
region             = "pakistan"           # pakistan / uae / usa
timezone           = "Asia/Karachi"

AI CONFIGURATION
──────────────────────────────────────────────
preferred_model    = "qwen-2.5-72b"       # which LLM (Bifrost routes)
monthly_budget     = "50"                 # USD - Bifrost spending limit
agent_name         = "Sarah"              # AI agent persona name
agent_personality  = "professional"       # professional / friendly / formal

CAPABILITIES SELECTION (true/false)
──────────────────────────────────────────────
voice_conversation         = true
whatsapp_conversational    = true
appointment_booking        = true
faq_support                = true
lead_qualification         = false
document_processing        = false
inventory_management       = false
hr_selfservice             = false
proactive_notifications    = true
visual_intelligence        = false
payment_processing         = false
email_automation           = false
predictive_analytics       = false
attendance_access          = false
contract_esigning          = false
multichannel_routing       = false
agent_escalation           = true
multilingual               = true        # auto-enabled if language != english

CHANNEL CONFIGURATION
──────────────────────────────────────────────
whatsapp_number    = "+923001234567"
voice_number       = "+92111234567"
web_chat           = false
email_inbound      = false

INTEGRATIONS
──────────────────────────────────────────────
erp_type           = "erpnext"           # erpnext / odoo / none
erp_url            = "http://..."
erp_api_key        = "<key>"
calendar_type      = "google"           # google / microsoft / calcom / none
calendar_id        = "xxx@gmail.com"
crm_type           = "twenty"           # twenty / suite / none
payment_gateway    = "jazzcash"         # jazzcash / stripe / none

AWS RESOURCES
──────────────────────────────────────────────
create_s3_backup   = true
create_cloudfront  = true
create_ses_domain  = false
```

---

### What new-client.py Creates Automatically vs Manually

```
AUTOMATED (zero human intervention):
  ✅ Keycloak tenant
  ✅ Qdrant collection named {client_id}-knowledge
  ✅ Supabase schema + row-level security policies
  ✅ Bifrost virtual key with monthly budget
  ✅ Paperclip company + agent entry
  ✅ Langfuse project (empty prompt template)
  ✅ n8n main workflow cloned from industry template
  ✅ All n8n variables filled from form fields
  ✅ Selected capabilities enabled in workflow
  ✅ Unselected capabilities disabled
  ✅ SIP extension in Asterisk for voice number
  ✅ WhatsApp webhook registered with Meta API
  ✅ AWS S3 bucket (if selected)
  ✅ AWS CloudFront distribution (if selected)

MANUAL (human required — cannot be automated):
  ❌ System prompt content in Langfuse
     (needs real client info: doctor names, hours, prices)
     TIME: 15-20 minutes

  ❌ Knowledge base documents uploaded to Qdrant
     (FAQs, SOPs, pricing, schedules from client)
     TIME: 20-30 minutes

  ❌ End-to-end test call + WhatsApp test
     TIME: 15 minutes
```

---

### script output example

```
┌─────────────────────────────────────────────────┐
│ AIOS NEW CLIENT ONBOARDED                       │
│ ─────────────────────────────────────────────── │
│ Client ID:    clinic-abc                        │
│ Industry:     Clinic                            │
│ Agent Name:   Sarah                             │
│ Language:     Urdu + English                    │
│ ─────────────────────────────────────────────── │
│ Keycloak tenant:     clinic-abc           ✅    │
│ Qdrant collection:   clinic-abc-knowledge ✅    │
│ Supabase schema:     clinic_abc           ✅    │
│ Bifrost key:         clinic-abc-key       ✅    │
│ Budget limit:        $50/month            ✅    │
│ Paperclip company:   Clinic ABC           ✅    │
│ n8n workflow:        clinic-abc-main      ✅    │
│ Capabilities:        5 enabled            ✅    │
│ WhatsApp webhook:    registered           ✅    │
│ Asterisk SIP:        +92111234567         ✅    │
│ AWS S3:              clinic-abc-backup    ✅    │
│ ─────────────────────────────────────────────── │
│ MANUAL STEPS REMAINING (45 min):               │
│ 1. Fill prompt → http://langfuse/clinic-abc    │
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

## 17. PHASE 1 LAB — EXACT DELIVERABLES

### What Must Be Built in 45 Days

```
WEEK 1 (Days 1-7): Infrastructure setup
  Both machines — Ubuntu 24.04 installed
  KVM setup — OPNsense VM + Issabel VM running
  Docker Layer A deployed (FOSS apps)
  Docker Layer B deployed (AI core)
  Inference Server — vLLM + Frigate running
  WireGuard tunnel between machines
  All services accessible via Dashy

WEEK 2 (Days 8-14): Capability templates — batch 1
  cap-voice-conversation.json
  cap-whatsapp-conversational.json
  cap-appointment-booking.json
  cap-multilingual.json
  cap-intent-detection.json
  cap-faq-support.json

WEEK 3 (Days 15-21): Capability templates — batch 2
  cap-lead-qualification.json
  cap-document-processing.json
  cap-inventory-management.json
  cap-hr-selfservice.json
  cap-proactive-notifications.json
  cap-agent-escalation.json

WEEK 4 (Days 22-28): Remaining capabilities + first use case templates
  cap-automated-reporting.json
  cap-visual-intelligence.json
  cap-payment-processing.json
  cap-email-automation.json
  cap-multilingual.json
  cap-attendance-access.json
  cap-contract-esigning.json
  cap-multichannel-routing.json
  cap-predictive-analytics.json
  cap-system-integration.json
  template-clinic-main.json      ← first use case template
  template-hr-main.json

WEEK 5-6 (Days 29-45): Remaining use case templates + first client
  template-realestate-main.json
  template-retail-main.json
  template-accounting-main.json
  template-pharmacy-main.json
  template-hotel-main.json
  template-callcentre-main.json
  template-legal-main.json
  template-academy-main.json
  template-security-main.json
  template-logistics-main.json
  new-client.py script built + tested
  First real client deployed end-to-end
  All demos working and tested
```

### Definition of Done for Each Capability Template
```
✅ Sub-workflow created in n8n
✅ All inputs are variables (zero hardcoding)
✅ All external calls go through Bifrost
✅ All data queries go through Qdrant (collection_id variable)
✅ All prompts pulled from Langfuse (prompt_key variable)
✅ Success + failure outputs defined
✅ Langfuse logging added
✅ Tested with at least 2 different client variable sets
✅ Documented in /docs/capabilities/[name].md
```

### Definition of Done for Each Use Case Template
```
✅ Main workflow created in n8n
✅ All client variables defined and documented
✅ Correct capabilities chained in correct order
✅ Intent routing logic complete (IF/SWITCH nodes)
✅ All capability calls pass correct variables
✅ Logging to Supabase + Langfuse at end
✅ Tested with dummy client data
✅ new-client.py supports this industry type
✅ Documented in /docs/use-cases/[name].md
```

---

*Section 15-17 added: Capabilities technical definition, n8n folder structure,*
*chaining explanation, new client form fields, Phase 1 deliverables.*
*Added: May 2026*
