# AIOS — Session Checkpoint

**Version:** 6.3
**Date:** June 12, 2026
**Branch:** main
**Last commit:** b45e9f9 (not pushed)

---

## Container Status (Server — June 12 after reboot recovery)

### Running (47 — all services healthy or starting)
aios-traefik, aios-postgres, aios-redis, aios-qdrant, aios-minio, aios-clickhouse, aios-ollama, aios-bifrost, aios-langfuse, aios-docling, aios-mem0, aios-asterisk, aios-dnsmasq-tftp, aios-knowledge-ingest, aios-knowledge-compile, aios-dograh-api, aios-dograh-ui, aios-tts-router, aios-chatterbox, aios-kokoro, aios-xtts-urdu, aios-whisper-stt, aios-n8n, aios-n8n-worker-1, aios-n8n-worker-2, aios-n8n-db, aios-flowise, aios-open-webui, aios-keycloak, aios-mcp, aios-vault, aios-vault-unseal, aios-grafana, aios-portainer, aios-dashy, aios-prometheus, aios-cadvisor, aios-node-exporter, aios-loki, aios-crowdsec, aios-frigate, aios-mosquitto, aios-gitops, aios-hermes, aios-speaches, aios-dia-tts, aios-data-qdrant-proxy

### Known Issues
- Chatterbox: runs with model loaded on CUDA but Docker healthcheck marks unhealthy
- Keycloak: health: starting (takes ~2min to become healthy)
- WireGuard: Created state (sysctl `net.ipv4.conf.all.src_valid_mark` not allowed in host network namespace — pre-existing, user wants to keep)
- dia-tts: Build context created on server, image built, container running but on CPU (Quadro M4000 can't run CUDA 12.x required by PyTorch 2.6)

### Written but NOT started
- Nextcloud (10.70.0.30), Odoo (10.70.0.20), Metabase (10.70.0.40) — docker-compose-apps.yml exists, never started

### Container Count: 47 running (1 building: dia-tts initially missing)

---

## Compose File Separation

| File | Contents | Status |
|------|----------|--------|
| `docker-compose-aios.yml` | AI infrastructure + orchestration: Traefik, Postgres, Redis, Qdrant, MinIO, Bifrost, Langfuse, Ollama, Asterisk, Dograh, n8n, Flowise, Open WebUI, CrowdSec, Grafana, Portainer, Speaches, Dia-TTS, etc. | **Running** (47 containers) |
| `docker-compose-apps.yml` | FOSS business apps: Nextcloud, Odoo, Metabase | **Never started** |

---

## Session History (Chronological)

### Session 1 — June 6: Voice Agent Pipeline Setup

[Session 1 content unchanged — items 1-7]

#### 1. Whisper STT — Upgraded to `large-v3` ✅
— (unchanged)

#### 2. XTTS Voice Cloning ✅
— (unchanged)

#### 3. Dograh ARI Integration ✅
— (unchanged)

#### 4. n8n — Fixed Secure Cookie ✅
— (unchanged)

#### 5. Dograh UI Login — Fixed ✅
— (unchanged)

#### 6. Architecture Reset — Dograh Replaces AGI ✅
— (unchanged)

#### 7. Git — Committed & Pushed ✅
— (unchanged)

---

### Session 2 — June 6: Voice Agent End-to-End

[Session 2 content unchanged — items 8-11]

#### 8. Dograh Workflow Created: "AI Voice Receptionist" ✅
— (unchanged)

#### 9. ARI WebSocket Tested — Events Flowing ✅
— (unchanged)

#### 10. Stasis(dograh) Dialplan Configured ✅
— (unchanged)

#### 11. End-to-End Voice Pipeline Ready for Testing ✅
— (unchanged)

---

### Session 3 — June 8: ElevenLabs TTS via TTS Router

[Session 3 content unchanged — items 12-16]

#### 12. ElevenLabs TTS — Switched from WebSocket to REST API via TTS Router ✅
— (unchanged)

#### 13. Fixed Audio Sample Rate Mismatch ✅
— (unchanged)

#### 14. Dockerfile: Added ffmpeg ✅
— (unchanged)

#### 15. Dograh Workflow Greeting Extended ✅
— (unchanged)

#### 16. STT: Switched to Deepgram Nova-3 Urdu ✅
— (unchanged)

---

### Session 4 — June 11: Deepgram STT + Ghost Cleanup

[Session 4 content unchanged — items 17-23]

#### 17. Deepgram API Key — Configured ✅
— (unchanged)

#### 18. STT Provider — Switched to Deepgram Nova-3 Urdu (org 2) ✅
— (unchanged)

#### 19. Workflow 1 (English) — Edges Fixed ✅
— (unchanged)

#### 20. Workflow 5 (Urdu) — Created ✅
— (unchanged)

#### 21. Ghost Config 5 / Org 3 — Removed ✅
— (unchanged)

#### 22. TTS Base URL — Fixed (`/v1` Prefix) ✅
— (unchanged)

#### 23. End-to-End Voice Pipeline Verified (Local Channel Test) ✅
— (unchanged)

---

### Session 5 — June 12: Server Reboot Recovery + AWS Infrastructure

#### 24. Server Reboot — Stack Completely Down ✅
- Server at 10.0.0.100 rebooted (uptime 2 min). Zero containers running.
- Docker daemon running but no compose stack started — systemd `aios-stack.service` failed.

#### 25. Root Cause: Missing dia-tts Build Context ✅
- `aios-stack.service` failed: `unable to prepare context: path "/aios/configs/dia-tts" not found`
- `docker-compose-aios.yml` on disk had uncommitted dia-tts service referencing build context that didn't exist on server
- **Fix**: Created `/aios/configs/dia-tts/` on server with `Dockerfile.dia`, `requirements.txt`, `server.py` (3 files, 2.8KB)
- dia-tts image built (PyTorch 2.6 CPU ~766MB download). Container runs CPU-only since Quadro M4000 can't use CUDA 12.x.

#### 26. Stack Restarted — 47 Containers Running ✅
- `docker compose -f /aios/docker-compose-aios.yml up -d` (with `--no-build` to skip dia-tts initially)
- All services came up: Traefik, Postgres, Qdrant, Redis, MinIO, Bifrost, Langfuse, Ollama, Asterisk, Dograh, n8n, Flowise, Open WebUI, CrowdSec, Grafana, Portainer, Speaches, Kokoro, Chatterbox, XTTS, Whisper, MCP, Mem0, Docling, Frigate, Mosquitto, Keycloak, Vault, GitOps, Hermes, etc.

#### 27. Hermes Agent — Fixed ✅
- Container in `Restarting (126)` loop — `exec /scripts/hermes.sh: Permission denied`
- **Root cause**: Hermes script lost executable permission (file permissions reset after server reboot? Not normal — likely the git pull replaced the file)
- **Fix**: `chmod +x /aios/scripts/hermes.sh` + `docker restart aios-hermes`
- Running stable (Up 1h+)

#### 28. Portainer — Fixed ✅
- Container running but `HTTP 307` redirect + security timeout: "Portainer instance timed out for security purposes"
- **Root cause**: Portainer auto-locks if admin not initialized
- **Fix**: `docker restart aios-portainer` — cleared security timeout
- Also added host port mapping `9000:9000` to compose (was missing — only on internal network 10.60.0.50)
- Changed Docker socket mount from `:ro` (read-only) to writable for environment management
- Accessible at `http://10.0.0.100:9000`

#### 29. AWS CLI — Installed & Configured ✅
- AWS CLI v2 installed on server (10.0.0.100)
- IAM credentials from `aios_accessKeys.csv`: AKIA565H4TDW4RHSX7TJ
- Account: 959740418285, IAM user: `aios`
- Region: us-east-1

#### 30. EC2 Key Pair — Created ✅
- EC2 key pair `aios-key` created in AWS
- Private key saved to `/aios/aios-key.pem` on server (chmod 400)

#### 31. EC2 Instance — Launched (Free Tier) ✅
- Instance ID: `i-01b37e00dfe0fc251`
- Type: `t3.micro` (2 vCPU, 1GB RAM, free tier)
- Public IP: `3.91.2.202`
- AMI: Ubuntu 22.04 LTS (ami-0d7405d05f836d0d4)
- Zone: us-east-1a
- Tags: Name=aios-aws, Project=AIOS

#### 32. Docker Installed on AWS EC2 ✅
- Docker Engine 29.5.3 + Docker Compose v5.1.4 installed on t3.micro
- Docker compose files not yet transferred (1GB RAM insufficient for full stack)

#### 33. TTS Router — Rewritten to ElevenLabs Direct ✅
- Complete rewrite of `configs/tts-router/server.py`
- Old: Language-aware routing (Urdu→XTTS, English→Chatterbox, fallback→Kokoro)
- New: Direct ElevenLabs REST API proxy with MP3→raw PCM conversion
- Added `ffmpeg` to Dockerfile for format conversion
- Environment: `DIA_URL`, `XTTS_URL`, `CHATTERBOX_URL`, `KOKORO_URL` added

---

## AWS Infrastructure (Current)

| Resource | ID/Value | Status |
|----------|----------|--------|
| AWS Account | 959740418285 | Active |
| IAM User | aios | EC2FullAccess granted |
| Region | us-east-1 | Default |
| Key Pair | aios-key | Created, PEM at `/aios/aios-key.pem` |
| EC2 Instance | i-01b37e00dfe0fc251 | `t3.micro` at 3.91.2.202 |
| OS | Ubuntu 22.04 | Docker 29.5.3 installed |
| Note | t3.micro (1GB RAM) too small for full AIOS stack | Upgrade needed for deployment |

---

## Voice Pipeline Architecture (Current)

```
Caller → SIP → Asterisk → ARI → Dograh (voice orchestrator)
  Dograh handles:
    1. Receive audio from caller via ARI WebSocket
    2. STT: Deepgram Nova-3 Urdu (cloud) — replaces local Whisper
    3. LLM: Dograh provider → Bifrost (10.40.0.10:4000) → OpenRouter
    4. TTS: Speaches provider → TTS Router (10.40.0.33:8030)
       → ElevenLabs multilingual_v2 (cloud, REST API)
    5. Send audio back to caller via ARI

TTS Pipeline (via Speaches provider):
  user_config.tts.base_url = "http://10.40.0.33:8030/v1"
  SpeachesTTSService extends OpenAITTSService
  Request: POST {base_url}/audio/speech → POST /v1/audio/speech
  TTS Router POST to https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream
  Voice: hardcoded to ELEVENLABS_VOICE_ID = "Ukfq9vQ0QNLZ4MGK0Uxc"
  Returns: raw PCM s16le 24000Hz mono, audio/L16;rate=24000;channels=1
```

### Component Endpoints

| Component | Endpoint | Status |
|-----------|----------|--------|
| Whisper STT | `POST /asr` at 10.40.0.40:9000 | ✅ `large-v3`, English perfect |
| Bifrost LLM | `POST /v1/chat/completions` at 10.40.0.10:4000 | ✅ Routes via OpenRouter |
| TTS Router | `POST /v1/audio/speech` at 10.40.0.33:8030 | ✅ ElevenLabs backend, 24000Hz raw PCM |
| XTTS Urdu | `POST /v1/tts` at 10.40.0.32:8020 | ✅ Voice cloned with WhatsApp sample |
| Dia Urdu TTS | `POST /v1/audio/speech` at 10.40.0.34:8034 | ✅ New — GPU Urdu TTS (CPU fallback) |
| Deepgram STT | Cloud (WebSocket via API key) | ✅ Nova-3 Urdu configured |
| Speaches STT/TTS | `POST /v1/audio/speech` at 10.40.0.41:8141 | ✅ faster-whisper-large-v3 |
| Dograh API | 10.50.0.30:8000 | ✅ Connected via ARI WebSocket |
| Dograh UI | 10.50.0.31:3010 | ✅ Login working |
| Portainer | 10.0.0.100:9000 | ✅ Host port mapped |

### Asterisk Extensions

| Ext | Purpose | Routing | Status |
|-----|---------|---------|--------|
| 100 | Admin desk | Dial(PJSIP/100,30) | Unavailable |
| 101 | Softphone (10.0.0.11) | Dial(PJSIP/101,30) | Registered, Avail |
| 102 | AI Agent (English) | `Stasis(dograh)` → WF 1 | ✅ TTS verified |
| 103 | Test softphone | Dial(PJSIP/103,30) | Unavailable |
| 104 | Android softphone | Dial(PJSIP/104,30) | Unavailable |
| 105 | AI Agent (Urdu) | `Stasis(dograh)` → WF 5 | ✅ Routing configured |
| 9000 | Cisco 7962G (10.0.0.12) | Dial(PJSIP/9000,30) | Registered, Avail |

### Dograh Configuration

| Item | Detail |
|------|--------|
| Telephony Config ID 1 | Asterisk-Local, ARI provider, endpoint `http://10.0.0.100:8088`, org 2 |
| Phone Number Ext 102 | Linked to Workflow ID 1 (English), type: sip_extension |
| Phone Number Ext 105 | Linked to Workflow ID 5 (Urdu), type: sip_extension |
| Workflow ID 1 | "AI Voice Receptionist" (English), active, v2 (edges fixed) |
| Workflow ID 5 | "Urdu Voice Receptionist", active, v1 |
| User Config (user_id=2) | STT=Deepgram(nova-3,ur), TTS=Speaches(TTS Router:8030/v1), LLM=Dograh→Bifrost |
| ARI Status | `Active connections: 1 (configs: [1])` — org 2 only |

---

## Pending

| Item | Priority | Status |
|------|----------|--------|
| Test end-to-end call: dial 102 (English) from Cisco phone (Ext 9000) | **High** | 🟡 TTS fixed, routing fixed (org 3 removed). Physically dial 102 from lab |
| Test end-to-end call: dial 105 (Urdu) from Cisco phone (Ext 9000) | **High** | 🟡 Verify Urdu STT/TTS pipeline after cleanup |
| FOSS apps (Nextcloud, Odoo, Metabase) | Low | ❌ never started |
| Chatterbox healthcheck fix | Low | ❌ Container works, missing `/health` endpoint |
| Nightly backup cron | Low | ❌ script exists, no cron |
| Add FreePBX to docker-compose-apps.yml | Low | ❌ not deployed yet |
| Upgrade AWS EC2 to larger instance for AIOS deployment | Low | 🟡 t3.micro (1GB RAM) too small for full stack |
| Deploy AIOS docker-compose to AWS EC2 | Low | ❌ pending instance upgrade |

---

## Key Architectural Decisions

1. **Architecture reset**: AGI script was a hack. Proper stack is Asterisk (SIP only) → Dograh (ARI voice orchestrator with built-in pipeline) → AI models. Dograh was designed for this exact use case.
2. **Dograh chosen** because it natively supports Asterisk ARI as telephony provider (discovered via API schema `provider: "ari"` → `ARIConfigurationRequest`)
3. **GPU limitation**: Quadro M4000 (Maxwell CC 5.0) maxes at NVIDIA driver 470, CUDA 11.4. No CUDA 12.x support. Ollama bundles its own CUDA 12.x and works. Other containers (XTTS, Chatterbox, Dia-TTS with PyTorch 2.6) need explicit handling or run CPU-only.
4. **TTS pipeline**: All TTS through Speaches provider → TTS Router → ElevenLabs REST API. TTS Router hardcodes voice ID `Ukfq9vQ0QNLZ4MGK0Uxc` — `voice` param from Dograh is ignored.
5. **Bifrost auth**: LiteLLM v1.82.6 stores tokens in `LiteLLM_VerificationToken` (SHA256 hash). Use `os.environ/VAR` syntax in config.yaml, not `${VAR}`.
6. **Whisper STT API**: Uses `POST /asr` endpoint (not OpenAI `/v1/audio/transcriptions`). Fields: `audio_file` (form-data), `task` (transcribe/translate), `language` (ISO code), `output` (txt/vtt/srt/tsv/json).
7. **Urdu STT bottleneck**: XTTS-generated Urdu speech is garbled — not recognizable by Whisper `large-v3` for transcription (though language detection now works correctly). Need better XTTS voice sample or alternative Urdu TTS.
8. **Deepgram STT preferred**: Cloud Deepgram Nova-3 Urdu replaces local Whisper for Urdu calls. Local Whisper `large-v3` stays as English fallback.
9. **Dograh user config**: TTS provider = `speaches` → `http://10.40.0.33:8030/v1` (must include `/v1`). STT provider = `deepgram` (Nova-3, Urdu). LLM = `dograh` → Bifrost.
10. **Deepgram API key**: Stored in `/aios/.env` as `DEEPGRAM_API_KEY`. Passed to `dograh-api` container via docker-compose env. Not in git.
11. **Org isolation in Dograh**: Dograh sends ARI StasisStart events to ALL connected org configurations. If multiple orgs have ARI configs on the same Asterisk instance, they compete for call handling. Orphan orgs without phone numbers hang up calls before the correct org can process them. Only one org should have an ARI config per Asterisk instance.
12. **Compose file separation**: `docker-compose-aios.yml` for AI infrastructure + orchestration, `docker-compose-apps.yml` for FOSS business apps (Odoo, Nextcloud, Metabase, FreePBX). Apps compose never started.
13. **Server auto-start**: Systemd `aios-stack.service` starts compose on boot. Failed June 12 due to missing dia-tts build context. Fixed by creating the build directory on server. Service uses `Type=oneshot`, `RemainAfterExit=yes`.
14. **AWS deployment**: AIOS can be deployed to AWS EC2. t3.micro free tier has only 1GB RAM — insufficient for full 47-container stack. Need g4dn.xlarge (or at least t3.medium) for production deployment. AWS CLI + key pair configured for automated deployment.
