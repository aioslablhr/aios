# AIOS — Session Checkpoint v5.0

## This Session (June 22) — Voice Layer Deep Dive & File Sync

### Voice Layer Audit — Running System Inspection
SSH'd to server at 10.0.0.100 and inspected every container, network, config, and database table:

**48 containers running** (up from 35 in May). Key additions: Speaches, Chatterbox, Kokoro, XTTS, DIA TTS, TTS Router, Open WebUI, Whisper STT, Mosquitto, N8N-worker-2.

**Traefik config deployed fresh** — 17 routes (was 2). All using Docker DNS names, no hardcoded IPs. Backups created on server.

**Open WebUI** moved from `aios-foss` to `aios-ai` zone (10.40.0.35) — correct architecture.

**Dograh DB inspected** — 2 active workflows found:
- Ext 102 (Shin Travels Sales Agent) — uses user defaults
- Ext 105 (Urdu Agent) — model_overrides for LLM/TTS

---

### Voice Layer — Full Pipeline Status

#### Running Voice Containers (all inspected)
| Container | Status | Purpose |
|-----------|--------|---------|
| aios-asterisk | ✅ healthy v22.9.0 | SIP PBX, ARI connected |
| aios-dograh-api | ✅ healthy v1.35.0 | Voice agent orchestration, ARI active |
| aios-dograh-ui | ✅ up | Agent management UI |
| aios-speaches | ✅ healthy | STT (faster-whisper-large-v3, UNUSED) |
| aios-chatterbox | ✅ up (GPU 4GB) | TTS (CUDA, UNUSED) |
| aios-kokoro | ✅ up | TTS CPU fallback, UNUSED |
| aios-tts-router | ✅ up v4.2.0 | Cloud-only TTS proxy (UpliftAI/ElevenLabs) |
| aios-xtts-urdu | ✅ up | Urdu TTS (CPU forced) |
| aios-dia-tts | ⚠️ broken | Model fails to load (Pydantic bug) |
| aios-whisper-stt | ✅ up | Legacy STT, ZOMBIE (unused) |
| aios-mosquitto | ✅ up | MQTT broker |

#### PJSIP Endpoints
7 defined. 2 registered: 101 (support trunk @ 10.0.0.11) and 9000 (Cisco phone, RTT 19ms).
2 AI agent extensions (102, 105) route to `Stasis(dograh)`.

#### Actual Provider Config (from Dograh DB user_configurations)
| Component | Provider | Location |
|-----------|----------|----------|
| STT | **Deepgram cloud** (nova-3-general) | Cloud — API key in DB |
| TTS | **ElevenLabs / UpliftAI cloud** | Cloud — API keys in DB/env |
| LLM | Speaches provider → **Bifrost** → OpenRouter | Local (Bifrost) → Cloud (OpenRouter) |

#### Call History
5 calls processed total. 1 successful test call logged: TTS served "Hello, thank you for calling SHIN Travels..." via UpliftAI.

---

### 17 Traefik Routes — All Deployed & Verified

| Route | Target | Docker DNS | Status |
|-------|--------|------------|--------|
| socialbeesai.com | Dashy | dashy:8080 | ✅ |
| admin.socialbeesai.com | Traefik Dashboard | traefik:8080 | ✅ |
| n8n.socialbeesai.com | n8n | n8n:5678 | ✅ |
| ai.socialbeesai.com | Bifrost | bifrost:4000 | ✅ |
| langfuse.socialbeesai.com | Langfuse | langfuse:3000 | ✅ |
| keycloak.socialbeesai.com | Keycloak | keycloak:8080 | ✅ |
| vault.socialbeesai.com | Vault | 10.0.0.100:8200 | ✅ |
| voice.socialbeesai.com | Dograh UI | dograh-ui:3010 | ✅ |
| app.socialbeesai.com | Flowise | flowise:3000 | ✅ |
| data.socialbeesai.com/minio | MinIO Console | data-minio-proxy:9001 | ✅ |
| grafana.socialbeesai.com | Grafana | grafana:3000 | ✅ |
| frigate.socialbeesai.com | Frigate | frigate:5000 | ✅ |
| clickhouse.socialbeesai.com | ClickHouse | clickhouse:8123 | ✅ |
| mcp.socialbeesai.com | MCP Server | mcp:8000 | ✅ |
| chat.socialbeesai.com | Open WebUI | open-webui:8080 | ✅ |
| portainer.socialbeesai.com | Portainer | portainer:9000 | ✅ |
| cadvisor.socialbeesai.com | cAdvisor | cadvisor:8080 | ✅ |

---

### Known Issues

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | **CrowdSec crash-looping** — duplicate YAML key in acquis.yaml | high | deferred |
| 2 | **GitOps agent crash-looping** — keeps dying ("Terminated") | high | deferred |
| 3 | **DIA TTS model fails to load** — Pydantic schema mismatch in dia library, `"loaded":false` | medium | unfixed |
| 4 | **STT uses Deepgram cloud** — Speaches local STT unused | low | local GPU can't handle it |
| 5 | **TTS uses UpliftAI/ElevenLabs cloud** — Chatterbox/Kokoro/XTTS unused | low | local GPU can't handle it |
| 6 | **API keys in DB plaintext** — ElevenLabs/Deepgram keys in user_configurations | medium | needs Vault migration |
| 7 | **Whisper STT zombie** — container runs, no workflow uses it | low | keep as offline fallback |
| 8 | **LLM provider label mismatch** — "speaches" provider with Bifrost URL | low | works correctly |
| 9 | **Workflow 102 has no model_overrides** — uses defaults, breaks silently if creds expire | medium | needs fix |
| 10 | **MinIO unhealthy** — health check failing | low | need investigation |
| 11 | **Keycloak health starting** — service works, probe too aggressive | low | minor |
| 12 | **CrowdSec 403** — all public endpoints blocked from external | medium | needs whitelist |
| 13 | **Prometheus targets down** — bifrost/n8n/frigate metrics endpoints missing | medium | needs /metrics |
| 14 | **Vault on host networking** — should be in aios-app zone | low | migration needed |
| 15 | **Open WebUI OLLAMA_BASE_URL points to Bifrost** — should be OPENAI_BASE_URL semantically | low | works but confusing |
| 16 | **chat_server.py** defined on disk, NOT running (port 8081 dead) | low | deferred |
| 17 | **Speaches on CPU image** — uses `latest-cpu`, GPU image available | low | local GPU can't handle |

---

### Next Steps

1. Fix CrowdSec acquis.yaml (add `-` list prefix to source blocks)
2. Fix GitOps agent crash-loop
3. Wire up Dograh patches (ari_manager.py, service_factory.py) — currently stock versions running
4. Start chat_server.py and wire to same RAG pipeline as voice agents
5. Fix DIA TTS model loading (upgrade dia library or switch model)
6. Add aios-foss network to Traefik (for future FOSS services)
7. Migrate API keys from DB to Vault

---

### Credentials Quick Ref

| Service | URL | Auth |
|---------|-----|------|
| Dashy | https://socialbeesai.com | — |
| n8n | https://n8n.socialbeesai.com | browser session |
| Bifrost | https://ai.socialbeesai.com | sk-aios-master-admin-key-change-me |
| Langfuse | https://langfuse.socialbeesai.com | create account |
| Keycloak | https://keycloak.socialbeesai.com | admin / admin |
| Vault | https://vault.socialbeesai.com | root token in .vault-keys |
| MinIO | https://data.socialbeesai.com/minio | admin / minioadmin |
| Grafana | https://grafana.socialbeesai.com | admin / grafana_admin_2026 |
| Dograh | https://voice.socialbeesai.com | sign up on first visit |
| Frigate | https://frigate.socialbeesai.com | — |
| Flowise | https://app.socialbeesai.com/flowise | admin / admin |
| Portainer | https://portainer.socialbeesai.com | create on first visit |
| Qdrant | https://qdrant.socialbeesai.com/dashboard | API key: aios_qdrant_2026 |
| ClickHouse | https://clickhouse.socialbeesai.com | default / clickhouse |
| Open WebUI | https://chat.socialbeesai.com | signup disabled |
| cAdvisor | https://cadvisor.socialbeesai.com | — |

Full creds: `docs/ref/credentials.md`

*Updated June 22, 2026 — AIOS Session Checkpoint v5.0*
