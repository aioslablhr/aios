# AIOS — Session Checkpoint

**Version:** 4.6
**Date:** June 3, 2026
**Branch:** main
**Last commit:** f7565f2 — deploy Qalb, Open WebUI, strip public routes

---

## Current State

### Infrastructure (Layer 1)
- Single-server architecture locked (no KVM, no OPNsense) — Docker + CrowdSec + Cloudflare = security equivalent
- 7 Docker network zones: DMZ (10.10), App (10.20), Data (10.30), AI (10.40), Voice (10.50), Mon (10.60), FOSS (10.70)
- WireGuard VPN deployed (lscr.io/linuxserver/wireguard) — LAN access via Dev PC
- Public: socialbeesai.com → Dashy, chat.socialbeesai.com → Open WebUI — everything else via LAN IP or WireGuard
- Bifrost (LiteLLM) as sole LLM gateway — all calls go through it
- Langfuse for observability, Prometheus + Grafana for infra metrics
- Qdrant vector store, PostgreSQL + Redis, MinIO S3
- CrowdSec WAF + Traefik + Cloudflare (DNS/SSL/DDoS)
- **36 active containers** (29 Layer A + 7 Layer B)

### AI Models (Local-First Hierarchy)
| Model | Task | VRAM | Zone |
|-------|------|------|------|
| Qalb-1.0-8B | Urdu LLM (primary) | ~5.5GB | AI (Ollama) |
| nomic-embed-text | Embeddings | ~0.3GB | AI (Ollama) |
| LLaVA 7B | Vision | ~4.5GB | AI (swaps w/ Qalb) |
| Chatterbox | English TTS (GPU) | ~1.5GB | AI (on-demand) |
| Kokoro | TTS (CPU fallback) | CPU | AI (on-demand) |
| XTTS-v2-Urdu-FT | Urdu TTS | ~2GB | AI (on-demand, new) |
| Whisper | STT | GPU | Voice (Frigate) |
| YOLO | Object detection | GPU | Voice (Frigate) |

### Voice Pipeline
- Asterisk + PJSIP (SIP trunking) → Dograh (orchestration) → Whisper (STT) → Bifrost (LLM) → Chatterbox/Kokoro (TTS)
- Dograh auto-selects TTS: Chatterbox (GPU primary) → Kokoro (CPU fallback)
- XTTS-v2-Urdu-FT added as Urdu TTS option (AI Zone, 10.40.0.32:8020)
- Cisco 7962G phone (ext 9000) fully working — TCP, registerWithProxy

### Memory & Knowledge
- mem0 with Qdrant backend — v2 API with multi-user isolation, session management, batch operations
- LLM Wiki compiler (compile-wiki.py) runs every 4 hours via knowledge-compile container (10.20.0.56)
- Knowledge ingestion (ingest-file.py) watches MinIO raw-uploads bucket

### FOSS Apps (Layer 2)
- **Nextcloud** (10.70.0.30) — file sync + collaboration, public: nextcloud.socialbeesai.com
- **Odoo** (10.70.0.20) — ERP, public: odoo.socialbeesai.com
- **Metabase** (10.70.0.40) — analytics/dashboards, public: metabase.socialbeesai.com
- Open WebUI (10.70.0.200) — client-facing AI chat, public: chat.socialbeesai.com
- All via docker-compose-apps.yml with Traefik auto-routing

---

## Architecture Decisions Locked
1. Single server (10.0.0.100, Quadro M4000 8GB) — no second machine
2. 7 Docker zones — Data Zone is `internal:true`
3. Local-first hierarchy — cloud is fallback only
4. All LLM calls through Bifrost (LiteLLM) — never direct API
5. Git = source of truth; GitOps auto-deploys from GitHub
6. No public infra ports — only Dashy + Open WebUI + FOSS apps
7. WireGuard VPN for admin access to all internal services
8. Nextcloud replaces Twenty CRM for file sync + collaboration
9. XTTS-v2-Urdu-FT as primary Urdu TTS (Coqui, GPU, on-demand)

---

## Known Issues
1. **n8n webhooks blocked**: Meta WhatsApp callbacks need a public URL — deferred until CRM workflow is built
2. **Qalb Modelfile conversion**: First-run conversion from HuggingFace safetensors to GGUF may take 5-15 min on Quadro M4000
3. **XTTS not yet deployed as container**: Server code, Dockerfile, and compose service written, but container not yet started (needs first `docker compose up`)
4. **FOSS apps not yet deployed**: Compose file written but containers not started
5. **No use case workflows**: n8n/workflows/ empty — 4 planned (Surveillance, HR/Payroll, CRM, Voice)

---

## Next Steps
1. `docker compose up` XTTS-v2-Urdu-FT and FOSS apps (Nextcloud, Odoo, Metabase)
2. WireGuard peer config retrieval + client setup on Dev PC
3. Industry stack standardization (clinic, real estate, retail, restaurant, hotel, education)
4. n8n workflow build (CRM/Sales first — WhatsApp → pipeline → closing)
5. Each use case gets a dedicated functional frontend dashboard
6. Backup strategy: automated nightly encrypted backups via MinIO + S3

---

## Resource Inventory
See `docs/INVENTORY.md` for complete service/port/credential/volume/dependency registry.

## Full Architecture Document
See `docs/PROJECT.md` (v4.0, 16 sections).
