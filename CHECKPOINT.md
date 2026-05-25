# AIOS — Build Checkpoint
## Last Updated: May 25, 2026 — n8n deployed + OpenRouter webhook test passed

---

### ✅ COMPLETED STEPS

**Phase 0-2 Foundation (all done):**
- GPU driver, Docker, 7 networks, data layer, security layer
- Vault initialized (shamir 5/3), KV v2 at `secret/`
- Git/GitHub, CI, GitOps, Hermes agent, dev scripts, Ansible
- Cloudflare tunnel + SSL + Dashy live on `socialbeesai.com`

**Asterisk PBX (compiled from source):**
- Asterisk 22.9.0 LTS, host networking, envsubst entrypoint for secret injection
- 6 extensions configured: 100 (Admin), 101 (Support), 102 (AI Agent), 103 (Test), 104 (Android), 9000 (Cisco)
- `pjsip.conf` + `extensions.conf` — clean, no hardcoded passwords
- Softphone-to-softphone calling works (101↔103, 103↔104)

**DNSmasq + TFTP for Cisco provisioning:**
- Container `aios-dnsmasq-tftp` on host network (port 69 UDP)
- Serves SEP + XMLDefault + dialplan + g3-tones + firmware files to phone
- `alternativeTftp=true` — phone fetches config from TFTP on every boot

**Cisco 7962G SIP Phone (MAC: 00:27:0D:C0:1C:92):**
- Firmware: SIP42.9-4-2SR3-1S (9.4.2SR3.1)
- ✅ **REGISTERS successfully** — shows green line key on "9000"
- ✅ **Calls OUT** — Cisco can dial any extension (100-104), works
- ✅ **Incoming calls FIXED** — switched SEP `<transportLayerProtocol>` from `2` (UDP) to `4` (TCP). TCP maintains persistent connection; Asterisk sends INVITEs over the same socket. Contact now shows `transport=TCP` with status `Avail`.
- **Root cause #1**: `disable_rport=yes` in pjsip.conf — phone needs rport in 200 OK Via
- **Root cause #2**: `proxy=USECALLMANAGER` mandatory — explicit IP kills REGISTER
- **Root cause #3**: UDP ephemeral sockets close immediately after REGISTER — TCP transport fixes this
- Full debug trail: `docs/capabilities/cisco-7962-provisioning.md`

**Asterisk fixes this session:**
- `maxload = 0.9` → `10.0` (was blocking ALL calls with 503 — server load was 1.28)
- Encoding corruption in configs cleaned → clean redeploy
- All 6 extensions added to both `pjsip.conf` and `extensions.conf`
- CI pipeline: YAML lint, compose validate, Trivy, secret scan

**n8n + OpenRouter (May 25):**
- n8n stack deployed: main (10.20.0.10:5678), n8n-db (10.20.0.15), worker-1 (10.20.0.13), worker-2 (10.20.0.12)
- Redis (10.30.0.30) added to docker-compose (was orphan)
- n8n admin created: `admin@socialbeesai.com` / `Aios_admin_2026`
- Workflow "AIOS - OpenRouter Test": Webhook → HTTP Request (OpenRouter) → Respond
- Webhook `POST /webhook/aios-test` passes messages as-is to OpenRouter, returns response
- Tested with `liquid/lfm-2.5-1.2b-instruct:free` → 200 OK, "Hello"
- Default model: `liquid/lfm-2.5-1.2b-instruct:free`; override via `"model"` in body
- `.env` updated with: `N8N_DB_PASSWORD`, `N8N_ENCRYPTION_KEY`, `OPENROUTER_API_KEY`
- Architecture decision: **Direct OpenRouter** (no Bifrost for cloud models) — LiteLLM 1.82.6 lacks OpenRouter provider

---

### ❌ KNOWN ISSUES

- **Vault on host networking** — needs move to `aios-app` network (port 8200 conflict)
- **Orphan containers** — Traefik, Dashy, Keycloak, CrowdSec, MinIO not in docker-compose. Deployed manually.
- **Chat/data subdomains return 504** — no backend yet
- **TRUNK_PASS still placeholder** — no SIP trunk configured
- **Vault unseal keys** — stored in `/aios/.vault-keys` (plaintext). Needs encrypted backup.
- **n8n admin user created** — but no API key (scopes require enterprise license). Using session cookie for API.
- **OpenRouter free tier rate limits** — workflow works but returns 429 on free models under heavy use.

---

### ✅ ARCHITECTURE DECISIONS — May 25, 2026

- **Inference:** OpenRouter primary + Claude fallback through Bifrost. No local LLM models on Quadro M4000 (8GB VRAM cannot compete with OpenRouter's free tier). GPU repurposed for embeddings (nomic-embed-text), STT (Whisper), vision (LLaVA), and TTS (Chatterbox).
- **Voice:** Dograh (self-hosted OSS, BSD-2) replaces Retell AI/Vapi for voice agent orchestration. Chatterbox AI (self-hosted OSS, MIT) replaces ElevenLabs for TTS/voice cloning. Both run on local infra — data sovereignty for regulated clients.
- **Knowledge:** LLM Wiki pattern (Karpathy, April 2026) replaces pure RAG for client knowledge bases. Obsidian vault as raw source → LLM compiles structured wiki pages at ingest time → agent reads compiled wiki at query time. Qdrant reserved for overflow/volatile data (conversations, temp cache). This works because client knowledge bases are <50k tokens.
- **Full updated architecture documented in CLAUDE.md (7 layers including Knowledge sub-layer).**

### ⬅ NEXT SESSION — Resume Here

**Phase 1 — Security Foundation:**
1. Deploy WireGuard container (10.20.0.90) — emergency remote access
2. Move Vault from host networking to `aios-app` network (fix port 8200 conflict)
3. Migrate first secrets from `.env` to Vault (Cloudflare API key first)
4. Add orphan containers to docker-compose (Redis, MinIO, Traefik, CrowdSec, Dashy, Keycloak)
5. Add missing compose services: n8n, n8n-workers, Flowise, Paperclip, WireGuard

**Phase 2 — Inference Layer:**
6. Get real OpenRouter API key, strip local LLM models from Ollama
7. Rewrite Bifrost config.yaml — OpenRouter primary, Claude fallback only
8. Verify: n8n → Bifrost → OpenRouter → Langfuse log in <3s
9. Set up Bifrost per-client virtual keys + budget controls

**Phase 3 — Data Hardening + Knowledge:**
10. Set up Obsidian vault → LLM Wiki compiler for client knowledge
11. Replace pure RAG with LLM Wiki + Qdrant hybrid pattern
12. Create MinIO bucket langfuse-events
13. Verify aios-data network internal:true enforced

**Phase 4 — Voice Stack:**
14. Deploy Dograh (10.50.0.30) — self-hosted voice agent orchestration
15. Deploy Chatterbox AI (10.40.0.30) — local GPU TTS + voice cloning
16. Wire pipeline: Asterisk → Dograh → Bifrost → OpenRouter → Chatterbox
17. Test: SIP phone call → AI agent response → works end-to-end

**Phase 5 — Orchestration (The Product):**
18. ✅ Deploy n8n + 2 workers with Redis queue
19. ✅ Wire n8n → OpenRouter webhook (tested: `POST /webhook/aios-test` → 200)
20. Build 6 core capability sub-workflows
21. Build first main workflow: template-clinic-main.json
22. Test: WhatsApp → n8n → OpenRouter → response

**Phase 6 — MCP & Tools:**
22. Deploy MCP servers: Supabase, Qdrant, WhatsApp, Filesystem
23. Wire MCP into n8n sub-workflows (replace raw HTTP calls)

**Phase 7 — Monitoring + Go-Live:**
24. Deploy Prometheus, Grafana, Loki, Portainer, Uptime Kuma
25. Complete new-client.py — onboard first real client

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
Containers: 13 (postgres, qdrant, redis, minio, vault, keycloak,
              traefik, crowdsec, gitops, hermes, dashy, asterisk, dnsmasq-tftp)
Disk:     953.9GB NVMe (850GB free)
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
