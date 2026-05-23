# AIOS — Build Checkpoint
## Last Updated: May 23, 2026 — Cisco 7962: FULLY WORKING (TCP transport fixed incoming calls)

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

---

### ❌ KNOWN ISSUES

- **Vault on host networking** — needs move to `aios-app` network (port 8200 conflict)
- **Orphan containers** — Traefik, Dashy, Keycloak, CrowdSec, Redis, MinIO not in docker-compose. Deployed manually.
- **Chat/data subdomains return 504** — no backend yet
- **TRUNK_PASS still placeholder** — no SIP trunk configured
- **Vault unseal keys** — stored in `/aios/.vault-keys` (plaintext). Needs encrypted backup.

---

### ⬅ NEXT SESSION — Resume Here

**Phase 3 — AI Core (high priority):**
1. Move Vault from host networking to `aios-app` network (fix port 8200 conflict)
2. Migrate first secrets from `.env` to Vault (Cloudflare API key first)
3. Deploy Langfuse (10.60.0.10) — LLM observability + prompt registry
4. Deploy Bifrost (10.40.0.10) — AI Gateway for ALL LLM calls
5. Deploy vLLM (10.40.0.40) — local inference on Quadro M4000 (Mistral 7B, Llama 3 8B, Qwen 2.5 7B)
6. Deploy Ollama (10.40.0.20) — dev inference (LLaVA 7B, nomic-embed-text)
7. Deploy n8n + Flowise (10.20.0.x) — orchestration

**Phase 4 — Monitoring + Voice:**
8. Deploy Prometheus, Grafana, Loki, Portainer, Uptime Kuma

**Phase 5 — Go-Live:**
9. Deploy FOSS apps (ERPNext, Metabase, etc.)
10. Build n8n workflow templates (20 capability sub-workflows)
11. Integrate WhatsApp, Retell AI, Deepgram, ElevenLabs
12. First client onboarding via `new-client.py`

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
