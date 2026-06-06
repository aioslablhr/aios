# AIOS — Session Checkpoint

**Version:** 6.0
**Date:** June 6, 2026
**Branch:** main
**Last commit:** 69fe5b1 (pending)

---

## Container Status (Server)

### Running (44 — all services healthy or starting)
aios-traefik, aios-postgres, aios-redis, aios-qdrant, aios-minio, aios-clickhouse, aios-ollama, aios-bifrost, aios-langfuse, aios-docling, aios-mem0, aios-asterisk, aios-dnsmasq-tftp, aios-knowledge-ingest, aios-knowledge-compile, aios-dograh-api, aios-dograh-ui, aios-tts-router, aios-chatterbox, aios-kokoro, aios-xtts-urdu, aios-whisper-stt, aios-n8n, aios-n8n-worker-1, aios-n8n-worker-2, aios-n8n-db, aios-flowise, aios-open-webui, aios-keycloak, aios-mcp, aios-vault, aios-vault-unseal, aios-grafana, aios-portainer, aios-dashy, aios-prometheus, aios-cadvisor, aios-node-exporter, aios-loki, aios-crowdsec, aios-frigate, aios-mosquitto, aios-gitops, aios-hermes, aios-data-minio-proxy, aios-data-qdrant-proxy

### Known Issues
- Chatterbox: runs with model loaded on CUDA but Docker healthcheck marks unhealthy
- Keycloak: health: starting (takes ~2min to become healthy)
- Hermes: running (was exit 126, fixed via chmod)
- WireGuard: Created state (sysctl `net.ipv4.conf.all.src_valid_mark` not allowed in host network namespace — pre-existing, user wants to keep)

### Written but NOT started
- Nextcloud (10.70.0.30), Odoo (10.70.0.20), Metabase (10.70.0.40) — docker-compose-apps.yml exists, never started

### Container Count: 45 (44 running, 1 created/non-functional)

---

## What's Done This Session (June 6 — Voice Agent Pipeline)

### 1. Whisper STT — Upgraded to `large-v3` ✅
- Switched from `medium` (1.5GB) → `large-v3` (3GB, ~7.8GB RSS) at 10.40.0.40:9000
- English STT verified perfect: "Hello, can you help me book an appointment for tomorrow"
- Urdu STT: `medium` detected English (wrong), `large-v3` now correctly detects Urdu but still can't transcribe accurately — root cause is XTTS-generated Urdu audio quality, not Whisper model size

### 2. XTTS Voice Cloning ✅
- Received WhatsApp voice note (PTT-20260606-WA0032.mp3, ~30s, Urdu)
- Converted to 24kHz WAV, replaced `/app/model_cache/default_speaker.wav` in XTTS container
- New voice sample helped: STT detects language as Urdu (was Chinese before), but XTTS output still garbled for accurate transcription
- **Bottleneck confirmed**: XTTS Urdu output quality is the limiting factor, not Whisper model size

### 3. Dograh ARI Integration ✅
- Discovered Dograh has native Asterisk ARI support (`ARIConfigurationRequest` schema with `provider: ari`)
- Created Dograh ARI telephony config (`Asterisk-Local`, config ID 1): endpoint `http://10.0.0.100:8088`, app name `dograh`
- Fixed Asterisk `http.conf` — removed `prefix = asterisk` so ARI WebSocket URL resolves at root
- Added ARI user `dograh` with password to `ari.conf`
- Dograh ARI WebSocket connected successfully: `[ARI org=2] WebSocket connected to http://10.0.0.100:8088`

### 4. n8n — Fixed Secure Cookie ✅
- Added `N8N_SECURE_COOKIE: "false"` to compose (was using HTTPS-only cookies in HTTP context)
- Password reset: inserted bcrypt hash directly into n8n Postgres DB
- Login working: `admin@socialbeesai.com` / `admin123`

### 5. Dograh UI Login — Fixed ✅
- **Root cause**: UI's Next.js rewrite rule sends API calls to `http://api:8000` — hostname `api` didn't resolve in Docker DNS
- **Fix**: Added `api` as network alias to `dograh-api` in `aios-voice` network
- Login verified working: `http://10.50.0.31:3010` with `admin@socialbeesai.com` / `admin123`

### 6. Architecture Reset — Dograh Replaces AGI ✅
- **Decision**: AGI script hack is wrong. Correct architecture is:
  - Asterisk (SIP core only) → Dograh (ARI voice orchestrator with native STT/LLM/TTS pipeline) → AI models
  - Dograh's built-in STT (configurable), LLM (via Bifrost), TTS (via Speaches/TTS Router)
- AGI script at `/var/lib/asterisk/agi-bin/ai-agent.agi` deprecating in favor of Dograh Stasis routing

### 7. Git — Committed & Pushed ✅
- Commit `69fe5b1`: whisper STT, kokoro compose entry, systemd auto-start, crowdsec configs, test scripts
- 231 files, 7004 insertions, 1294 deletions
- Pushed to GitHub main branch

## What's Done This Session (June 6 — Session 2: Voice Agent End-to-End)

### 8. Dograh Workflow Created: "AI Voice Receptionist" ✅
- Workflow ID 1, status: active, version 1 (published)
- 3 nodes: startCall → agentNode → endCall
- Phone number (Ext 102) created on telephony config ID 1
  - `inbound_workflow_id: 1`, linked to Workflow ID 1
  - Address: "102", type: sip_extension, country: PK
- Full workflow definition verified via Dograh API

### 9. ARI WebSocket Tested — Events Flowing ✅
- Dograh receives all ARI events from Asterisk: ChannelCreated, ChannelDialplan, Dial, ChannelStateChange, StasisStart
- WebSocket connects and stays connected through container restarts
- Active connections: 1 (config: 1, org: 2)

### 10. Stasis(dograh) Dialplan Configured ✅
- Ext 102 routing changed from `AGI(ai-agent.agi)` → `Stasis(dograh)` (no Answer() before Stasis)
- **Critical insight**: Dograh's ARI handler has TWO code paths:
  - **Inbound (state=Ring)**: Looks up phone number → finds workflow → creates run → answers call → starts pipeline
  - **Outbound (state=Up)**: Requires explicit `workflow_run_id=X,workflow_id=X,user_id=X` in Stasis args as key=value pairs
  - Removing `Answer()` from dialplan ensures calls enter Stasis as "Ring" → inbound handler fires

### 11. End-to-End Voice Pipeline Ready for Testing ✅
- ARI connection: ✅ (WebSocket connected, events flowing)
- Dialplan routing: ✅ (Ext 102 → Stasis(dograh))
- Workflow: ✅ (ID 1, active, 3 nodes)
- Phone number mapping: ✅ (Ext 102 → Workflow ID 1)
- User config: ✅ (LLM → Bifrost, TTS → Speaches, STT → Dograh built-in)
- Test pending: physically dial 102 from Cisco phone (Ext 9000) to trigger inbound handler

---

## Voice Pipeline Architecture (Current)

```
Caller → SIP → Asterisk → ARI → Dograh (voice orchestrator)
  Dograh handles:
    1. Receive audio from caller via ARI WebSocket
    2. STT: configurable (Dograh built-in, or external)
    3. LLM: via Bifrost → OpenRouter (general-reasoning route)
    4. TTS: via Speaches provider → TTS Router (10.40.0.33:8030)
       Urdu → XTTS, English → Chatterbox/Kokoro
    5. Send audio back to caller via ARI
```

### Component Endpoints

| Component | Endpoint | Status |
|-----------|----------|--------|
| Whisper STT | `POST /asr` with `audio_file` (form-data) at 10.40.0.40:9000 | ✅ `large-v3`, English perfect, Urdu limited by TTS quality |
| Bifrost LLM | `POST /v1/chat/completions` with Bearer token at 10.40.0.10:4000 | ✅ Routes via OpenRouter |
| TTS Router | `POST /v1/audio/speech` (OpenAI-compatible) at 10.40.0.33:8030 | ✅ All backends working |
| XTTS Urdu | `POST /v1/tts` at 10.40.0.32:8020 | ✅ Voice cloned with WhatsApp sample, quality TBD |
| Dograh API | 10.50.0.30:8000 | ✅ Connected via ARI WebSocket |
| Dograh UI | 10.50.0.31:3010 | ✅ Login working |

### Asterisk Extensions
- **Ext 100**: Admin
- **Ext 101**: Softphone (10.0.0.11)
- **Ext 102**: AI Agent — `Stasis(dograh)` → Dograh ARI inbound handler → Workflow ID 1
- **Ext 9000**: Cisco 7962G (registered, sip:9000@10.0.0.100)

### Dograh Configuration
| Item | Detail |
|------|--------|
| Telephony Config ID 1 | Asterisk-Local, ARI provider, endpoint `http://10.0.0.100:8088` |
| Phone Number ID 1 | Ext 102, linked to Workflow ID 1, type: sip_extension |
| Workflow ID 1 | "AI Voice Receptionist", status: active, 3 nodes |
| User Config | LLM=Dograh→Bifrost, TTS=Speaches(10.40.0.33:8030), STT=Dograh built-in |

---

## Pending

| Item | Priority | Status |
|------|----------|--------|
| Test end-to-end call: dial 102 from Cisco phone (Ext 9000) | **High** | 🔴 **Critical** — physical phone pick-up needed |
| Fix Urdu STT accuracy (better TTS / voice sample) | Medium | ❌ XTTS Urdu quality bottleneck |
| Chatterbox healthcheck fix | Low | ❌ Container works, missing `/health` endpoint |
| Nightly backup cron | Low | ❌ script exists, no cron |
| FOSS apps (Nextcloud, Odoo, Metabase) | Low | ❌ never started |

---

## Key Architectural Decisions

1. **Architecture reset**: AGI script was a hack. Proper stack is Asterisk (SIP only) → Dograh (ARI voice orchestrator with built-in pipeline) → AI models. Dograh was designed for this exact use case.
2. **Dograh chosen** because it natively supports Asterisk ARI as telephony provider (discovered via API schema `provider: "ari"` → `ARIConfigurationRequest`)
3. **GPU limitation**: Quadro M4000 (Maxwell CC 5.0) maxes at NVIDIA driver 470, CUDA 11.4. No CUDA 12.x support. Ollama bundles its own CUDA 12.x and works. Other containers (XTTS, Chatterbox) need explicit handling.
4. **TTS pipeline**: Urdu → XTTS, English → Chatterbox (GPU), fallback → Kokoro (CPU), routed by TTS Router (10.40.0.33:8030).
5. **Bifrost auth**: LiteLLM v1.82.6 stores tokens in `LiteLLM_VerificationToken` (SHA256 hash). Use `os.environ/VAR` syntax in config.yaml, not `${VAR}`.
6. **Whisper STT API**: Uses `POST /asr` endpoint (not OpenAI `/v1/audio/transcriptions`). Fields: `audio_file` (form-data), `task` (transcribe/translate), `language` (ISO code), `output` (txt/vtt/srt/tsv/json).
7. **Urdu STT bottleneck**: XTTS-generated Urdu speech is garbled — not recognizable by Whisper `large-v3` for transcription (though language detection now works correctly). Need better XTTS voice sample or alternative Urdu TTS.
8. **Dograh user config**: TTS provider already set to `speaches` → `http://10.40.0.33:8030`. STT provider set to `dograh` (built-in). LLM via Dograh provider → Bifrost.
