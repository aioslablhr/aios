# AIOS — End-to-End Deployment Plan
## Sequential build steps: bare metal to fully operational AIOS
### Server: 10.0.0.100 (Quadro M4000, 31GB RAM, 953GB NVMe)
### Dev PC: 10.0.0.13 (Windows, Docker Desktop)
### Order: Foundation → Core Infra → Dev Layer → AI → Orchestration → Monitoring → Voice/Visual → FOSS → Go-Live

---

## PHASE 0 — FOUNDATION

### STEP 1 — Install NVIDIA Quadro M4000 Driver

```
Server: SSH into 10.0.0.100

1.1  sudo apt update && sudo apt install nvidia-driver-470 -y
1.2  sudo reboot
1.3  nvidia-smi  # Verify: shows Quadro M4000, 8GB VRAM

1.4  sudo apt install nvidia-container-toolkit -y
1.5  sudo nvidia-ctk runtime configure --runtime=docker
1.6  sudo systemctl restart docker
1.7  docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
     # Verify: GPU accessible inside container
```

✅ Done when: `nvidia-smi` shows Quadro M4000 + Docker can access GPU

---

### STEP 2 — Install Docker Engine (if not installed)

```
2.1  sudo apt install docker.io docker-compose-v2 -y
2.2  sudo usermod -aG docker ai
2.3  newgrp docker
2.4  docker --version && docker compose version
```

✅ Done when: `docker run hello-world` works without sudo

---

## PHASE 1 — CORE INFRASTRUCTURE

### STEP 3 — Docker Networks + Directory Structure + .env

```
3.1  Create 7 Docker networks (one per zone):

     docker network create aios-dmz   --subnet=10.10.0.0/24
     docker network create aios-app   --subnet=10.20.0.0/24
     docker network create aios-data  --subnet=10.30.0.0/24 --internal
     docker network create aios-ai    --subnet=10.40.0.0/24
     docker network create aios-voice --subnet=10.50.0.0/24
     docker network create aios-mon   --subnet=10.60.0.0/24
     docker network create aios-foss  --subnet=10.70.0.0/24

3.2  mkdir -p /aios/{configs/{traefik,crowdsec,keycloak,bifrost,grafana},
          n8n/{workflow-templates/{capabilities,use-case-templates},clients,internal},
          langfuse/prompts,clients,scripts,data,ansible/roles,docs/capabilities}

3.3  scp .env ai@10.0.0.100:/aios/.env && chmod 600 /aios/.env
```

✅ Done when: `docker network ls` shows all 7 networks, /aios/ tree exists, .env secured

---

### STEP 4 — Deploy Data Layer

```
Containers on 10.30.0.0/24 (data zone, internal:true):
  PostgreSQL (10.30.0.10) — main operational database
  Qdrant     (10.30.0.20) — vector DB for RAG
  Redis      (10.30.0.30) — queue + cache
  MinIO      (10.30.0.40) — S3-compatible storage

4.1  Add data services to docker-compose-aios.yml
4.2  docker compose -f docker-compose-aios.yml up -d postgres qdrant redis minio
4.3  Verify: docker ps — all healthy
```

✅ Done when: All 4 data containers running and healthy

---

### STEP 5 — Deploy Security Layer

```
Containers:
  Vault     (10.20.0.50, app zone) — secrets management
  Keycloak  (10.20.0.40, app+data) — SSO/OIDC (uses Postgres)
  Traefik   (10.10.0.10, dmz+app+mon+foss) — reverse proxy
  CrowdSec  (10.10.0.11, dmz+app) — WAF

5.1  Add security services to docker-compose-aios.yml
5.2  docker compose up -d vault keycloak traefik crowdsec
5.3  Initialize Vault — store all API keys
5.4  Configure Traefik — Cloudflare DNS challenge, Let's Encrypt SSL
5.5  Configure Keycloak — master realm, create admin user
```

✅ Done when: All 4 containers running, Traefik serves HTTPS, Keycloak admin accessible

---

## PHASE 2 — DEVELOPMENT LAYER (moved up per v4.0 priority)

### STEP 6 — Git Init + GitHub Remote

```
6.1  cd /aios && git init
6.2  Create .gitignore (no .env, no secrets, no data/)
6.3  git add . && git commit -m "AIOS v4.0 — initial commit"
6.4  Create GitHub repository: aios
6.5  git remote add origin git@github.com:[org]/aios.git
6.6  git push -u origin main
```

✅ Done when: All AIOS code on GitHub, GitOps workflow ready

---

### STEP 7 — GitHub Actions Runner + CI Pipeline

```
7.1  Create self-hosted runner on server (or use GitHub-hosted)
7.2  Create .github/workflows/ci.yml with:
     - yamllint on docker-compose files
     - Trivy vulnerability scan on containers
     - Python syntax check on /scripts/
     - Network config validation
7.3  Push and verify CI passes
```

✅ Done when: Push triggers CI, pipeline passes, Trivy scans clean

---

### STEP 8 — GitOps Agent GitOps Deployment

```
Container on 10.20.0.100 (app zone):

8.1  Add GitOps Agent to docker-compose-aios.yml
8.2  docker compose up -d gitops
8.3  Polls GitHub every 30s, auto-deploys on change
8.4  Auto-deploy: docker-compose-aios.yml + all configs

✅ Done when: `docker logs aios-gitops` shows "Watching github.com:aioslablhr/aios.git every 30s"

---

### STEP 9 — Hermes Agent (Autonomous Ops)

```
Container on 10.20.0.70 (app zone):

9.1  Add Hermes Agent to docker-compose-aios.yml
9.2  docker compose up -d hermes
9.3  Configure: health checks, auto-restart, disk/memory alerts
9.4  Configure Slack/Telegram notification channel
```

✅ Done when: Hermes monitors all containers, alerts on failures

---

### STEP 9.5 — Dev Scripts + Docs Init

```
9.5.1  Create /aios/scripts/ directory with:
       - openclaw.py          # AIOS Lab Assistant (Dev PC CLI)
       - new-client.py         # Client onboarding (Vault + Keycloak + Qdrant + n8n)
       - backup.py             # Nightly encrypted backups → S3/NAS
       - health-check.py       # On-demand system health report
       - disaster-recovery.py  # Full restore from backup

9.5.2  Create /aios/docs/capabilities/ directory

9.5.3  Document in CLAUDE.md:
       - Adding a New Capability Sub-Workflow (9 steps)
       - Adding a New Use Case Main Workflow (8 steps)
       - Scripts reference table
```

✅ Done when: Scripts directory populated, doc templates created

---

## PHASE 3 — AI CORE

### STEP 10 — Deploy AI Layer (GPU)

```
Containers on 10.40.0.0/24 (AI zone):
  Ollama    (10.40.0.20) — dev inference with GPU
  LiteLLM   (10.40.0.30) — dev gateway
  vLLM      (10.40.0.40) — production inference with GPU
  Bifrost   (10.40.0.10) — production AI gateway
  Langfuse  (10.60.0.10, mon zone) — observability

10.1 Add GPU services to docker-compose-aios.yml
10.2 docker compose up -d ollama
10.3 ollama pull mistral:7b-q4
10.4 ollama pull llama3:8b
10.5 ollama pull qwen2.5:7b
10.6 ollama pull llava:7b
10.7 ollama pull nomic-embed-text
10.8 docker compose up -d vllm    # Production inference with GPU
10.9 docker compose up -d bifrost # Production gateway
10.10 docker compose up -d langfuse
```

✅ Done when: Ollama serves models, vLLM responds on :8000, Bifrost routes requests

---

### STEP 11 — Deploy Orchestration

```
Containers on 10.20.0.0/24 (app zone):
  n8n + 2 workers  (10.20.0.10-.12) — master orchestrator
  Flowise           (10.20.0.20) — visual agent builder
  Dify              (10.20.0.21) — LLM app platform
  Paperclip         (10.20.0.60) — AI company OS
  Open WebUI        (10.20.0.30) — chat UI

11.1 Add orchestration services to docker-compose-aios.yml
11.2 docker compose up -d n8n n8n-worker-1 n8n-worker-2
11.3 docker compose up -d flowise dify paperclip open-webui
```

✅ Done when: All orchestration containers running, n8n web UI accessible

---

## PHASE 4 — MONITORING + VOICE + VISUAL

### STEP 12 — Deploy Monitoring

```
Containers on 10.60.0.0/24 (mon zone):
  Prometheus        (10.60.0.20) — metrics
  Grafana           (10.60.0.30) — visualisation
  Loki              (10.60.0.40) — logs
  Portainer         (10.60.0.50) — Docker management
  Dashy             (10.60.0.70) — homepage
  Uptime Kuma       (10.60.0.60) — uptime monitoring
  Dozzle            (10.60.0.80) — live logs
  nvidia-smi exp.   (10.60.0.90) — GPU metrics
  Watchtower        (10.60.0.110) — auto-updates

12.1 Add monitoring services to docker-compose-aios.yml
12.2 docker compose up -d prometheus grafana loki
12.3 docker compose up -d portainer dashy uptime-kuma dozzle
12.4 docker compose up -d nvidia-smi-exporter watchtower
```

✅ Done when: Grafana shows GPU metrics, Dashy links all tools

---

### STEP 13 — Deploy Voice Layer

```
Containers on 10.50.0.0/24 (voice zone):
  MQTT Mosquitto  (10.50.0.20) — event bus
  Asterisk PBX    (10.50.0.10) — VoIP engine

13.1 Add voice services to docker-compose-aios.yml
13.2 docker compose up -d mqtt asterisk
13.3 Configure Asterisk SIP extensions
13.4 Register Cisco IP Phone on LAN → SIP extension
```

✅ Done when: Cisco phone shows registered, MQTT pub/sub works

---

### STEP 14 — Deploy Visual AI

```
Containers (app zone):
  Frigate NVR    (10.20.0.90) — object detection with GPU
  go2rtc         (10.20.0.91) — RTSP stream management

14.1 Add Frigate + go2rtc to docker-compose-aios.yml (GPU passthrough)
14.2 docker compose up -d go2rtc frigate
14.3 Connect 2 IP cameras via RTSP
14.4 Configure YOLO model for detection
```

✅ Done when: Camera feeds visible in Frigate, object detection firing

---

## PHASE 5 — FOSS APPS + GO-LIVE

### STEP 15 — Deploy FOSS Apps

```
Separate stack: docker-compose-apps.yml on 10.70.0.0/24

15.1 Create /aios/docker-compose-apps.yml
15.2 Start with ERPNext + Metabase (core client apps)
15.3 Add others per client need: Calcom, Twenty CRM, Paperless-ngx, etc.
```

✅ Done when: FOSS apps accessible via Traefik subdomains

---

### STEP 16 — Integrate External Services

```
16.1 Configure Cloudflare DNS → Traefik (subdomains)
16.2 Connect WhatsApp Business API → n8n webhook
16.3 Connect Retell AI → Asterisk SIP
16.4 Connect Deepgram + ElevenLabs → voice pipeline
16.5 Configure AWS S3 nightly encrypted backups
```

✅ Done when: WhatsApp trigger → agent responds, Voice call → AI answers

---

### STEP 17 — Build n8n Workflow Templates

```
17.1 Build 20 capability sub-workflows in n8n
     (cap-voice-conversation, cap-whatsapp-conversational, etc.)
17.2 Build 12 use case main workflow templates
     (template-clinic-main, template-hr-main, etc.)
17.3 Build new-client.py automation script
```

✅ Done when: All capabilities tested, new-client.py can onboard a client in 10 min

---

### STEP 18 — First Client Go-Live

```
18.1 Run new-client.py for client
18.2 Fill prompt in Langfuse (15 min)
18.3 Upload knowledge docs → Qdrant (20 min)
18.4 Test WhatsApp → Test Voice → Demo → Sign-off
```

✅ Done when: Paying client live on the platform

---

### Progress Dashboard

```
Phase          Steps                         Status        Notes
──────────────────────────────────────────────────────────────────────────
PHASE 0 Foundation
  STEP 1   GPU Driver                          ✅
  STEP 2   Docker Engine                       ✅
PHASE 1 Core Infra
  STEP 3   Networks + Dirs + .env              ✅
  STEP 4   Data Layer (4 containers)           ✅
  STEP 5   Security Layer (4 containers)       ✅           Vault needs init
PHASE 2 Dev Layer
  STEP 6   Git init + GitHub push              ✅
  STEP 7   GitHub Actions + CI                 ✅
  STEP 8   GitOps Agent                        ✅
  STEP 9   Hermes Agent                        ✅
  STEP 9.5 Dev Scripts + Docs Init             ✅
PHASE 3 AI Core
  STEP 10  AI Layer (GPU)                      ⬜
  STEP 11  Orchestration                       ⬜
PHASE 4 Monitor + Voice + Visual
  STEP 12  Monitoring                          🟡           Dashy done (10.60.0.70)
  STEP 13  Voice Layer                         ✅           Asterisk + 6 extensions + TFTP,
  STEP 13  Voice Layer                         ✅             Cisco 7962 registers + calls OUT + calls IN,
  STEP 13  Voice Layer                         ✅             TCP transport (SEP transportLayerProtocol=4)
  STEP 14  Visual AI                           ⬜
PHASE 5 FOSS + Go-Live
  STEP 15  FOSS Apps                           ⬜
  STEP 16  Integrations                        🟡           Cloudflare tunnel + DNS done
  STEP 17  n8n Workflows                       ⬜
  STEP 18  First Client                        ⬜
──────────────────────────────────────────────────────────────────────────
Total: 18 steps across 5 phases
Legend: ✅ Complete  🟡 Partial  🔶 In Progress  ⬜ Not Started
```
