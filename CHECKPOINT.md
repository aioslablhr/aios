# AIOS — Session Checkpoint

**Version:** 10.1
**Date:** June 22, 2026
**Branch:** main
**Last commit:** adeb949

---

## Container Status (Server — June 22, 2026)

### Running (54 — all services healthy)
aios-asterisk, aios-bifrost, aios-cadvisor, aios-chatterbox, aios-chatwoot-db, aios-chatwoot-redis, aios-chatwoot-web, aios-chatwoot-worker, aios-clickhouse, aios-crowdsec, aios-dashy, aios-data-minio-proxy, aios-data-qdrant-proxy, aios-dia-tts, aios-dnsmasq-tftp, aios-docling, aios-dograh-api, aios-dograh-ui, aios-flowise, aios-frigate, aios-gitops, aios-grafana, aios-hermes, aios-keycloak, aios-knowledge-compile, aios-knowledge-ingest, aios-kokoro, aios-langfuse, aios-llm-proxy, aios-loki, aios-mcp, aios-mem0, aios-minio, aios-mosquitto, aios-n8n, aios-n8n-db, aios-n8n-worker-1, aios-n8n-worker-2, aios-node-exporter, aios-ollama, aios-open-webui, aios-portainer, aios-postgres, aios-prometheus, aios-qdrant, aios-redis, aios-speaches, aios-traefik, aios-tts-router, aios-vault, aios-vault-unseal, aios-whisper-stt, aios-wireguard, aios-xtts-urdu

### Known Issues
- Chatterbox: runs with model loaded on CUDA but Docker healthcheck marks unhealthy
- Keycloak: health: starting (takes ~2min to become healthy)
- WireGuard: Created state (sysctl `net.ipv4.conf.all.src_valid_mark` not allowed in host network namespace)
- dia-tts: CPU-only on Quadro M4000 (can't run CUDA 12.x)
- **TTS English words**: ElevenLabs voice mispronounces English words in Urdu
- **Chat server**: runs in screen session, not Docker (manual restart needed after reboot)

### Written but NOT started
- Nextcloud, Odoo, Metabase — docker-compose-apps.yml exists, never started

### Container Count: 54 running

---

## Compose File Separation

| File | Contents | Status |
|------|----------|--------|
| `docker-compose-aios.yml` | AI infrastructure + orchestration: 54 containers across 8 zones | **Running** (54 containers) |
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

### Session 6 — June 13: LLM Proxy, Qalb Rejected, Qwen Rejected, Switched to Bifrost/OpenRouter Cloud

#### 34. Root Cause: Qalb 1.0-8b Does Not Support Tools ✅
- Ext 105 call: greeting plays → user speaks → Deepgram STT transcribes → Dograh sends tools → Qalb 400 error (`does not support tools`) → crash → hangup
- STT was working correctly all along (confirmed by direct Deepgram API test)
- **Fix**: Created `configs/llm-proxy/` — lightweight FastAPI proxy at 10.40.0.35:11435 that strips `tools` and `tool_choice` from requests before forwarding to Ollama

#### 35. Urdu Prompts — Grammar Fixed + Shortened ✅
- Rewrote all 3 workflow nodes for Workflow 5, greeting updated with "Social Bees AI" brand name

#### 36. Qalb 1.0-8b — REJECTED (Gibberish + Unusably Slow) ❌
- 16-29s TTFB (2.78 tok/s). Urdu outputs were nonsensical: introduced itself as "احمد خان", degraded into gibberish, finally gave up "مجھے افسوس ہے، میں آپ کی مدد کرنے نہیں سکتی۔"
- No tool support, terrible Urdu, unusably slow on Quadro M4000

#### 37. Qwen 2.5 7B — REJECTED (Also Gibberish + Slow) ❌
- Already pulled on Ollama (4.68GB, Q4_K_M). Tested at 7.08 tok/s (~2.5x faster than Qalb)
- BUT: Urdu output was equally bad — mixed Chinese characters (`窃取以下工具的信息，以便更好地回答用户问题`), English words mixed in (`velvet group`, `reception`), nonsensical sentences
- Both local models failed: Quadro M4000 (Maxwell 2015, 8GB VRAM) is too weak for any local Urdu LLM at usable quality

#### 38. Switched to Bifrost → OpenRouter Cloud (Multilingual) ✅
- Dograh config ID=2 updated: model=`multilingual`, base_url=`http://10.40.0.10:4000/v1`, api_key=`sk-aios-bifrost`
- Bifrost routes `multilingual` → OpenRouter free tier: Qwen 3 80B → Gemma 4 31B → Qwen 2.5 72B (with fallback chain)
- Created Bifrost virtual key `sk-aios-bifrost` for Dograh access
- Result: **Fast cloud inference, coherent native Urdu, culturally appropriate language**
- User confirmed: "much better, urdu native language is very good now"

#### 39. TTS: Google Tested → Back to ElevenLabs ✅
- Switched TTS to Google TTS (`voice="urdu"`) — user said "pathetic accent"
- Switched back to ElevenLabs (`voice="default"`, voice ID `G1gUElsVCoazUpfBnLnt`)
- Current TTS quality: OK for pure Urdu but **bad pronunciation of English words mixed in Urdu**
- In Pakistani Urdu, English words are commonly mixed in ("main ne meeting schedule kar di"). The ElevenLabs voice pronounces English words with wrong accent because it's not a native Urdu speaker
- **Next step**: Need a native Urdu ElevenLabs voice (voice cloning or different voice ID)

#### 40. LLM Prompts Updated for Native Pakistani Urdu ✅
- Main Conversation: "Speak only natural Pakistani Urdu. Use common Urdu phrases like جی، ٹھیک ہے، اچھا، بھئی. Keep responses short and conversational like a real person. Never mix in English or Hindi words."
- Start Call: "You are a Pakistani Urdu-speaking receptionist. Greet callers in natural Urdu with proper adab."
- These are separate from TTS — LLM language quality is now good, TTS accent is the remaining issue

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
    2. STT: Deepgram Nova-3 Urdu (cloud)
    3. LLM (Urdu/105): SpeachesLLMService → Bifrost (10.40.0.10:4000, model=multilingual) → OpenRouter free tier
       → Qwen 3 80B → Gemma 4 31B → Qwen 2.5 72B (with fallback chain)
       Fast cloud inference, coherent native Pakistani Urdu
    4. LLM (English/102): Dograh provider → Bifrost (10.40.0.10:4000) → OpenRouter
    5. TTS (all): Speaches provider → TTS Router (10.40.0.33:8030, voice-based routing)
       → voice="default" → ElevenLabs REST API (voice ID G1gUElsVCoazUpfBnLnt)
       → voice="urdu" → Google TTS (translate.googleapis.com, tl=ur)
    6. Send audio back to caller via ARI

TTS Pipeline (via Speaches provider):
  user_config.tts.base_url = "http://10.40.0.33:8030/v1"
  SpeachesTTSService extends OpenAITTSService
  TTS Router routes by voice name:
    default → ElevenLabs API (voice ID from env var ELEVENLABS_VOICE_ID)
    urdu/google/google_tts → Google Translate TTS
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
| Telephony Config ID 1 | Asterisk-Local, ARI provider, endpoint `http://10.0.0.100:8088`, org 1 |
| Phone Number Ext 102 | Linked to Workflow ID 1 (English), type: sip_extension |
| Phone Number Ext 105 | Linked to Workflow ID 5 (Urdu), type: sip_extension |
| Workflow ID 1 | "AI Voice Receptionist" (English), active, v2 |
| Workflow ID 5 | "Urdu Voice Receptionist", active, v1 |
| User Config (user_id=1) | **Single config for all workflows.** LLM=Speaches→Bifrost(multilingual, 10.40.0.10:4000), STT=Deepgram(nova-3,en), TTS=Speaches→TTS Router(10.40.0.33:8030, voice=default→ElevenLabs, speed=0.9). WF 5 overrides: stt.language=ur, tts.voice=uplift. |

---

## Pending

| Item | Priority | Status |
|------|----------|--------|
| Test end-to-end call: dial 102 (English) from Cisco phone (Ext 9000) | **High** | 🟡 Not tested yet |
| Test end-to-end call: dial 105 (Urdu) from Cisco phone (Ext 9000) | **Done** | ✅ LLM = Bifrost/OpenRouter multilingual (fast, native Urdu). TTS = ElevenLabs (accent OK for pure Urdu, bad on English words). Conversation flows naturally. |
| Get native Urdu ElevenLabs voice | **High** | 🟡 Current voice `G1gUElsVCoazUpfBnLnt` has poor pronunciation of English words mixed in Urdu. Need voice cloning or different voice ID. |
| FOSS apps (Nextcloud, Odoo, Metabase) | Low | ❌ never started |
| Chatterbox healthcheck fix | Low | ❌ Container works, missing `/health` endpoint |
| Nightly backup cron | Low | ❌ script exists, no cron |
| Add FreePBX to docker-compose-apps.yml | Low | ❌ not deployed yet |
| Upgrade AWS EC2 to larger instance for AIOS deployment | Low | 🟡 t3.micro (1GB RAM) too small for full stack |
| Deploy AIOS docker-compose to AWS EC2 | Low | ❌ pending instance upgrade |

---

13. **Knowledge strategy**: Two-tier approach in production:
    - **LLM Wiki** (primary) — Small knowledge bases (<50k tokens). Compiled once from raw docs into structured wiki, injected into agent prompt at session start. Used for Shin Travels (Ext 102) and Imperium (Ext 105). Faster (no vector search latency), cheaper, more reliable for this scale.
    - **Vector RAG via Qdrant** (secondary) — For future clients with large document sets (100k+ tokens). Uses Flowise UI or ingest pipeline (docling → knowledge-ingest → Qdrant). To be tested and validated after Wiki path is fully operational.
    - Both paths coexist. Wiki is default. RAG is available when needed.
14. **Odoo deployment**: Planned after voice agent knowledge layer is stable. Odoo integrates at runtime — Dograh agents query Odoo API live during calls (client lookup, booking status, payment verification). Not static data sync. Odoo lives in docker-compose-apps.yml (never started yet).

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
15. **LLM Proxy for Qalb**: Qalb 1.0-8b does not support OpenAI tool/function calling. Dograh sends tool definitions (hangup, transfer, etc.) with every LLM call, causing Qalb to error. Created `aios-llm-proxy` (10.40.0.35:11435) that strips `tools` and `tool_choice` from requests before forwarding to Ollama. Downside: tools like hangup are unavailable — call ends via LLM-determined end condition only.
16. **Qalb LLM rejected**: Qalb 1.0-8b was unusable — 2.78 tok/s (16-30s per turn), no tool support, gibberish Urdu responses. Replaced by Qwen 2.5 7B (7 tok/s, tools support, coherent Urdu). Qwen already pulled and available on Ollama. Switch involved: updating model name in `user_configurations.id=2`, reverting base_url from LLM proxy back to direct Ollama.
17. **Qwen 2.5 7B also rejected**: 7 tok/s on Quadro M4000 (2.5x faster than Qalb) but Urdu output was still gibberish with Chinese/English mixed in. Quadro M4000 is fundamentally too weak for any local Urdu LLM at usable quality.
18. **Bifrost/OpenRouter cloud for Urdu**: Final working LLM solution. Dograh → Bifrost (`model=multilingual`) → OpenRouter free tier. Routes to Qwen 3 80B → Gemma 4 31B → Qwen 2.5 72B with fallback. Fast cloud inference, coherent native Pakistani Urdu, free tier. Follows CLAUDE.md Bifrost routing principle (ALL LLM calls through Bifrost).
19. **Bifrost key management**: Virtual key `sk-aios-bifrost` created via Bifrost API for Dograh access. Master admin key is `sk-aios-master-admin-key-change-me`. Config reference: `/aios/configs/bifrost/config.yaml` has all model routing.
20. **TTS accent problem**: ElevenLabs voice `G1gUElsVCoazUpfBnLnt` handles pure Urdu OK but English words mixed in Urdu ("main ne meeting schedule kar di") are mispronounced. The voice is not a native Urdu speaker. Solution: voice cloning from a native Urdu speaker recording (2-3 min sample) or finding a better ElevenLabs voice ID.

---

### Session 7 — June 13: Urdu Call End-to-End Test + TTS Speed Fix

#### 41. TTS Router v4.0.0 — Verified Healthy ✅
- Rebuilt and running (container up, `/health` returns `{"status":"healthy"}`)
- Uses `--no-cache` to fully rebuild; second build used cache (ffmpeg layer cached, ~0.2s)

#### 42. Ext 105 Urdu Call — Tested End-to-End from Cisco 7962G ✅
- Caller (Ext 9000) dials 105 → Asterisk → Dograh ARI → Workflow 5 (Urdu)
- Greeting plays in Urdu
- User speaks Urdu → Deepgram Nova-3 transcribes
- LLM responds via Bifrost/OpenRouter multilingual chain
- TTS via TTS Router → ElevenLabs
- **Observed latency**: ~5.6s per turn (improved from ~8-9s in Session 6)
- Call ended with `call_duration_exceeded` (hit 5 min / 300s limit — now increased to 600s)

#### 43. Root Cause: Silent/No Reply After First Turn ✅
- Multiple factors combined:
  1. **VAD too sensitive (default 0.7)** — background noise from 2 devices triggered false speech detection mid-LLM response → Dograh thought user interrupted → early hangup
  2. **Context blowup** — noise triggers produced large prompts (5,257 tokens on last turn), causing 6.04s LLM TTFB
  3. **OpenRouter 429 rate limits** — Bifrost paid fallback model routing caused profuse errors
  4. **TTS speed=1.0 default** — no speed parameter passed, ElevenLabs default (normal speed) sounded choppy

#### 44. VAD Threshold — Increased to 0.85 ✅
- Edit: `/aios/dograh-api/run_pipeline.py` line 252: `VAD_THRESHOLD = 0.85` (was 0.70)
- Less sensitive to background noise, less false interrupt detection

#### 45. Max Call Duration — Increased to 600s ✅
- Docker env `MAX_CALL_DURATION=600` on `dograh-api` service in compose

#### 46. TTS Speed — Reduced to 0.8 ✅
- PostgreSQL: `UPDATE user_configurations SET config = jsonb_set(config, '{tts,speed}', '"0.8"') WHERE id = 2;`
- BUT: TTS Router was **not passing speed param** to ElevenLabs API — speed was always 1.0

#### 47. Bifrost Paid Fallback Models — Fixed (404 Tool Call Errors) ✅
- Original Bifrost config had `gemma-4-31b-it:free` and `qwen3-next-80b-a3b-instruct:free` as fallback models
- When free-tier rate limits hit, Bifrost tried paid models WITHOUT `:free` suffix → `qwen3-next-80b-a3b-instruct` and `gemma-4-31b-it` don't exist as standalone model IDs on OpenRouter → 404 errors
- **Fix**: Updated Bifrost config: `gemma-4-31b-it` (same model, drop `:free` suffix) and `qwen-3-80b` (correct name without `next`)
- Result: **Zero 404 errors**. No more tool calling failures.

#### 48. TTS Router `server.py` — Fixed Speed Pass-Through ✅
- `call_upliftai(text, speed=1.0)` now accepts and passes `speed` to Uplift AI API
- `payload["speed"] = speed` included when speed ≠ 1.0
- Rebuilt and deployed (cached build, container restarted)
- Verified via grep: speed parameter fully wired in server.py

#### Remaining: TTS English Words in Urdu
- ElevenLabs voice `G1gUElsVCoazUpfBnLnt` still mispronounces English words mixed in Pakistani Urdu
- Conversation quality is good — LLM Urdu is native, VAD is stable, latency ~5.6s
- Next: native Urdu ElevenLabs voice or voice cloning

---

### Session 7 (cont'd) — June 13: Paid Bifrost Chain, Latency Analysis

#### 49. Bifrost Model Chain — Paid Only (No More 404/429) ✅
- Removed all `:free` OpenRouter models (no tool support → 404 cascading failures)
- New chain: `google/gemma-4-31b-it` (paid) → `qwen/qwen3-next-80b-a3b-instruct` (paid) → `meta-llama/llama-3.3-70b-instruct` (paid)
- OpenRouter balance: $9.77 — cost per call ~$0.01-0.02, lasts hundreds of calls
- Zero 404/429 errors. Full tool support.
- **Bifrost restart required** — LiteLLM persists old models in DB, needed clean restart

#### 50. TTS Speed — Applied via ffmpeg atempo ✅
- Speed changed from 1.0 → **0.90** (10% slower)
- Applied via `-af "atempo=0.9"` in ffmpeg conversion — guaranteed, independent of Uplift AI support
- Verfied: POST /v1/audio/speech showing `speed=0.9` in logs

#### 51. VAD Threshold — 0.85 (Stable) ✅
- Increased from 0.7 to 0.85 — less false interrupt from background noise

#### 52. Call Duration — 1800s (30 min) ✅
- Hardcoded in `/app/api/services/pipecat/run_pipeline.py:344`
- Changed from 600 → 1800 via sed on running container
- Dograh API restarted to apply

#### 53. Uplift AI 503 Transient Outage ✅
- Uplift AI returned 503 Service Unavailable during one call
- TTS Router passed through 502 → Dograh pipeline errored
- Resolved on its own (transient upstream issue)

#### 54. Latency Analysis — 3 Remaining Bottlenecks 🔴

From run_id=175 exact timestamps:

| Step | Time | % of total |
|------|------|-----------|
| User stops speaking | 0s | — |
| LLM TTFB (first call) | **2.55s** | 51% |
| Speaches pipeline overhead | **0.91s** | 18% |
| TTS generation (Uplift AI) | **1.52s** | 30% |
| **Total → audio plays** | **~5.0s** | 100% |

Subsequent turns: LLM TTFB drops to 1.06s → total ~3.5s

**Fix 1 — TTS Router Connection Pooling** 🔴
- TTS Router creates a new httpx.AsyncClient() per request
- Reuse a shared client with connection pooling → eliminate TLS handshake (~300-500ms)
- Reduces TTS latency by ~25-33%
- **File**: `configs/tts-router/server.py` — move `httpx.AsyncClient` to module-level singleton

**Fix 2 — Larger TTS Chunks** 🔴
- Dograh splits LLM responses into small chunks (4-150 chars) 
- Each chunk = 1 Uplift AI API call = 1.5s round trip
- Average response: 3-5 chunks = 4.5-7.5s total TTS time
- Reducing chunk count by 50% would cut total TTS time by ~40%
- **Requires**: Dograh Speaches provider TTS aggregation config

**Fix 3 — Professional Urdu Prompt** 🟡
- Current prompts are basic (greeting, conversation, tools)
- Pro prompt with: natural fillers ("اہ...", "جی جی"), conversational flow, cultural tone, confusion handling
- Transform *quality* — caller feels like talking to a person
- **Do after latency fixed** — good prompt wasted on 5s pause

---

## Voice Pipeline Architecture (Updated — June 13)

```
Caller → SIP → Asterisk → ARI → Dograh (voice orchestrator)
  Dograh handles:
    1. Receive audio from caller via ARI WebSocket
    2. STT: Deepgram Nova-3 (cloud) — ~0.5s TTFB
       → Base config: language=en
       → WF 5 override: language=ur
    3. LLM (all workflows): SpeachesLLMService → Bifrost (10.40.0.10:4000, model=multilingual)
       → PAID: Gemma 4 31B → Qwen 3 80B → Llama 3.3 70B
       → TTFB: ~1-2.5s (2.55s first call warmup, ~1.06s subsequent)
    4. TTS (base): Speaches → TTS Router (10.40.0.33:8030, voice=default → ElevenLabs, speed=0.90)
       → WF 5 override: voice=uplift → Uplift AI API
       → Speed=0.90 via ffmpeg atempo (local post-processing)
       → Processing time: ~1.5-2s per chunk
    5. Send audio back to caller via ARI WebSocket

Total per-turn latency: ~5s (first) / ~3.5s (subsequent)
  Bottlenecks: LLM TTFB (51%), TTS (30%), Speaches pipeline overhead (18%)

Config resolution: workflow.user_id → user_configurations → resolve_effective_config(workflow_definitions.workflow_configurations.model_overrides)
  → Single org (org 1), single user (user 1: socialbeesaios@gmail.com)
```

---

## Key Architectural Decision #21
- **TTS speed handling**: Dograh sends `speed` in TTS request payload via Speaches provider but TTS Router was ignoring it. Fix: explicit `speed` parameter in `call_upliftai()` function. Lesson: parameters must be explicitly forwarded through proxy layers — they are not automatically passed through.

## Key Architectural Decision #22
- **Paid OpenRouter > free**: Free tier (`:free` suffix) on OpenRouter does NOT support tool/function calling for most models. Dograh sends tool definitions (hangup, transfer) with every LLM call. Free models return 404 → Bifrost cascades through fallbacks → 5-10s extra latency per turn. Paid models ($9.77 balance, $0.01-0.02/call) support tools natively, zero 404s, no rate limits.

## Key Architectural Decision #23
- **ffmpeg atempo for TTS speed**: Rather than relying on upstream TTS providers (Uplift AI, ElevenLabs) to support the `speed` parameter correctly, apply `atempo` filter in ffmpeg post-processing in TTS Router. Guaranteed speed control independent of provider support.

## Key Architectural Decision #24
- **Connection pooling for TTS Router**: Current implementation creates a new `httpx.AsyncClient()` for every TTS request. This means a new TCP connection + TLS handshake per request (~300-500ms overhead). Fix: shared module-level client with connection pooling. Applied as part of latency optimization sprint.

---

## Session 7 — Knowledge Layer: LLM Wiki (June 16)

### Completed
- Analyzed current data layer (Postgres pgvector, Qdrant, Redis, MinIO, Mem0, Docling, Knowledge-Ingest, Knowledge-Compile)
- Identified gaps vs vision doc: Elasticsearch, `/query` endpoint, BGE reranker, Guardrails — all deferred (premature optimization)
- Created `knowledge/SCHEMA.md` — 3 page types (concept/entity/source), linking rules, quality bar
- Created 4 templates in `knowledge/templates/` — concept.md, entity.md, source.md, index.md
- Created `knowledge/scrape-website.py` — crawls URL → markdown in raw/
- Rewrote `knowledge/compile-wiki.py` — line-by-line parser with `--company` flag
- Fixed: config.yaml Bifrost URL from 10.40.0.10:4000 (unreachable from data zone) to `bifrost:4000` (Docker DNS)
- Fixed: LLM model from `gemma-4-31b` (401 forbidden) to `general-reasoning`
- Fixed: index.md saved at wiki root (category="" → `wiki_dir / "" if "" else wiki_dir`)
- Compiled Shin Travels wiki: 5 pages (2 concepts + 1 entity + 1 source + index)
- Pipeline: scrape → compile, end-to-end working
- All commits pushed: `knowledge/SCHEMA.md`, templates, scraper, compiler, config

### Known Issues
- Container `/app/companies` is NOT bind-mounted — compiled wiki is ephemeral inside container. Must manually `docker cp` to host after each compile. Docker compose needs `- /aios/knowledge/companies:/app/companies` volume mount.
- `scrape-website.py` runs inside container (requires Python deps). No host-level `pip3` available on server.
- Shin Travels website (`shintravels.co.uk`) is a 3KB placeholder page — wiki content is generated/inferred by LLM. Needs real business documents for meaningful wiki.
- Server local modifications (stashed on June 16): asterisk, bifrost, tts-router, xtts configs — not committed. Git reset forced after stash failed (permission on `crowdsec/hub/.index.json`). Those config changes are lost.
- LLM output is non-deterministic — each compile produces slightly different content (page count varies 2-5)

---

## Session 8 — Shin Travels: Extension 2000 AI Voice Agent (June 16)

### Completed
- Created Dograh organization 4 (Shin Travels), user 4, phone number 2000
- Created workflow 6 (Shin Travels): Start Call → Agent Node → End Call, published
- Added PJSIP endpoint/auth/aor for extension 2000 in `pjsip.conf`
- Added dialplan entry `exten => 2000,Stasis(dograh)` in `extensions.conf`
- Fixed `http.conf`: removed `prefix = asterisk` (Dograh ARI manager doesn't support it)
- Fixed `ari.conf`: added `[dograh]` user for Dograh ARI authentication
- Configured user 4 with: dograh LLM, deepgram STT (nova-3-general, en), speaches TTS
- Updated workflow 6 configs to match: speaches TTS, deepgram STT, dograh LLM
- **Patched `ari_manager.py`**: changed `_handle_inbound_stasis_start` to skip (not hangup) when extension doesn't match current config. Both Social Bees (org 2) and Shin Travels (org 4) share Stasis app `dograh` — without this patch, first config to receive the event hangs up before the correct config can handle it.
- Mounted patched `dograh-patches/ari_manager.py` as bind volume in docker-compose
- Added `EXT_2000_SECRET` to Asterisk environment in docker-compose
- Verified end-to-end pipeline: Asterisk → ARI → Dograh pipeline → STT (Deepgram) → LLM (Dograh) → TTS (Speaches) → audio back to caller — run 205 completed successfully

### Known Issues (Session 8)
- `ari_manager.py` patch is only needed for multi-org setups sharing the same Stasis app — currently unnecessary with single org
- EXT_2000_SECRET must be in `.env` file (gitignored) and in Asterisk container env vars

---

## Session 9 — Dograh Org Consolidation (June 17)

### Completed
- Consolidated all Dograh data into a single org (org 1) with single user (user 1: socialbeesaios@gmail.com)
- Deleted org 2, org 4, user 2, user 4 (test artifacts from development)
- Moved all workflows (WF 1 English, WF 5 Urdu, WF 6 Shin Travels) → org 1, user 1
- Moved telephony config, phone numbers, external credentials → org 1
- Merged usage cycle history → org 1
- **Updated User Config 1** (single master config):
  - LLM: Speaches → Bifrost (multilingual, 10.40.0.10:4000) — ALL workflows now use local gateway
  - STT: Deepgram Nova-3 (en) — base language English
  - TTS: Speaches → TTS Router (voice=default → ElevenLabs, speed=0.9)
- **Added WF 5 overrides** for Urdu: `workflow_configurations.model_overrides` → stt.language=ur, tts.voice=uplift
- Added phone number Ext 2000 → WF 6 (Shin Travels) under org 1
- Removed `ari_manager.py` multi-org patch dependency (single org, no Stasis event competition)

### Config Resolution Chain (simplified)
```
Inbound call → phone_number.inbound_workflow_id → workflows.user_id → user_configurations
  → resolve_effective_config(workflow_definitions.workflow_configurations.model_overrides)
  → final effective config
```
- All 3 workflows use the same base User Config (id=1)
- WF 5 (Urdu) additionally merges: `{stt: {language: ur}, tts: {voice: uplift}}`
- WF 1 (English) and WF 6 (Shin Travels) use base config unchanged
- Workflow 6 uses text greeting, not audio file greeting

---

## Session 10 — June 17: Ext 102 SHIN Travels Sales Agent + Chatwoot CRM

### Completed

#### 55. Factory Reset Dograh + Fresh Setup ✅
- Dropped `dograh` database, recreated with clean schema via Alembic migrations
- Fresh user `socialbeesaios@gmail.com` / `aiosadmin2026`, org 1 auto-created
- Dograh pinned to `1.35.0` in docker-compose
- Login loop fixed: `secure:!0` → `secure:!1` in Next.js route handlers

#### 56. User Config — Local Providers ✅
```json
LLM: speaches → Bifrost (10.40.0.10:4000/v1, model=frontier-reasoning, api_key=sk-aios-master-admin-key-change-me)
STT: deepgram (nova-3-general, en-GB, api_key=fe444a27a666a3e471b8002ff56be87f964b9938)
TTS: elevenlabs (voice=pFZP5JQG7iQjIQuC4Bku / Lily, model=eleven_flash_v2_5)
```

#### 57. Ext 102 Workflow — Created & Tested ✅
- 3-node workflow: Welcome & Qualify → Travel Sales Conversation → End Call
- Greeting: "Hello, thank you for calling SHIN Travels. This is Emma speaking."
- ARI WebSocket connected to Asterisk (dograh-ws, port 8088)
- Test call succeeded: greeting plays (UK accent), STT transcribes, LLM responds, TTS speaks
- **Pipeline errors fixed**: STT was calling Speaches `/audio/transcriptions` (404) — switched to Deepgram

#### 58. Call Duration — Extended to 15 min ✅
- 3 limits found and patched:
  1. `audio_config.py:34` — `max_recording_duration_seconds` 300→900
  2. `pipeline_engine_callbacks_processor.py:26` — `max_call_duration_seconds` 300→900
  3. `workflow_configurations.max_call_duration` — set to 900 via API
- All patches saved to `/aios/dograh-patches/`

#### 59. Full Shin Travels Website Content Extracted ✅
- Deployed `browserless/chrome` (10.40.0.60) for headless JS rendering
- Scraped all 11 pages: home (18K chars), about, 6 articles, privacy, terms, cookies
- Total: ~40K chars of travel content

#### 60. LLM Wiki — Compiled ✅
Structured markdown wiki saved to `/aios/n8n/knowledge/shin-travels/wiki/`:
```
wiki/
├── index.md              — Company overview (3.3K)
├── concepts/
│   ├── destinations.md   — All destinations with details
│   └── services.md       — All services
├── entities/
│   └── packages.md       — Pricing, deals, FX rates, policies
├── source/
│   └── raw-scraped.txt   — Full raw website content (40K)
├── faq.md                — 28 real-world FAQs
```

#### 61. Travel Sales System Prompt — 7,396 chars ✅
- Emma persona (UK female, SHIN Travels sales consultant)
- Complete sales methodology: Open → Qualify → Recommend → Handle Objections → Close → Capture Lead
- All Shin Travels knowledge embedded (destinations, pricing, Umrah, policies)
- Scripted objection handling (price, visa, safety, timing)
- Published as workflow v3

#### 62. Chatwoot CRM — Deployed & Connected ✅
- Deployed `chatwoot/chatwoot:latest` with `pgvector/pgvector:pg16` DB
- Services: chatwoot-db (10.70.0.55), chatwoot-redis (10.70.0.56), chatwoot-web (10.70.0.50), chatwoot-worker
- URL: `http://10.0.0.100:8070/` or `https://chatwoot.socialbeesai.com`
- Admin: `socialbeesaios@gmail.com` / `LahorePakistan@2026`
- "Call Transcripts" inbox created (ID 1, identifier `8xXig1ed5a9Ps4hQVjuMsrSL`)
- API token: `S25Q5AkyFCGwUrXUzzn8SCYw`

#### 63. Dograh → Chatwoot Transcript Sync ✅
- Script: `/aios/scripts/dograh_to_chatwoot.py` — polls Dograh API for new runs
- Cron: runs every minute, auto-pushes transcripts to Chatwoot
- **31 conversations synced** (all past and new calls)
- Run 42 (latest call, 4377 chars) → Chatwoot conversation 31

#### 64. Standalone Emma Chat UI ✅
- Created at `http://10.0.0.100:8081/emma_chat.html`
- Dark-themed, standalone chat interface for Emma
- Uses Dograh text-chat API (workflow 1 sessions)
- Accessible without Dograh UI

#### 65. New Services Added
| Service | IP | Port | Purpose |
|---------|----|------|---------|
| browserless/chrome | 10.40.0.60 | 3000 | Headless browser for JS rendering |
| chatwoot-web | 10.70.0.50 | 3000 | Chatwoot CRM web UI |
| chatwoot-worker | 10.70.0.51 | — | Chatwoot background jobs |
| chatwoot-db | 10.70.0.55 | 5432 | Chatwoot PostgreSQL with pgvector |
| chatwoot-redis | 10.70.0.56 | 6379 | Chatwoot Redis cache |

### Known Issues
- ElevenLabs voice `pFZP5JQG7iQjIQuC4Bku` (Lily) is UK female but limited free-tier voice quality
- OpenRouter balance $0.11 — Claude Sonnet 4 costs ~$3/M input tokens, ~$15/M output tokens
- Hermes container in restart loop (unrelated to session changes)
- browserless/chrome container still running — stop when not needed

### Next Steps (Session 10)
- Switch TTS from ElevenLabs Lily to Chatterbox GPU TTS (better quality, free, local)
- Set up proper RAG pipeline: Qdrant ↔ MCP server ↔ Dograh tools
- Build client-facing dashboard in Metabase or Grafana
- Add lead capture workflow (n8n → Chatwoot → email/Slack)

---

## Session 11 — June 18: Emma v3 Prompt, Chatwoot Sync Fix, Emma Taylor Voice

### Completed

#### 66. Root Cause: Ext 102 Call Answer Delay (Model Routing) ✅
- Server reboot at ~10:53 UTC cleared VAD+model config; `multilingual` (Gemma 4 31B paid) doesn't support tool use on OpenRouter causing 6.7s fallback cascade
- **Fix**: Switched to `frontier-reasoning` (Claude Sonnet 4 / GPT-4o, paid, tool-native)
- Confirmed all override paths clean (user=DB, workflow=empty, org=empty)

#### 67. Real-time Chatwoot Sync — Built & Debugged ✅
- Module: `/aios/dograh-patches/chatwoot_sync.py` — fires inside `run_pipeline.py` `finally` block
- **3 bugs found and fixed:**
  1. **Network isolation**: dograh-api was on Voice/AI/Data zones but NOT FOSS zone. Chatwoot is on FOSS (10.70.0.50). Added `aios-foss` network to dograh-api in compose.
  2. **Phone E.164 validation**: Cisco Ext 9000 passes `"9000"` as caller_number. Chatwoot rejects non-E.164 numbers (`422`). Fix: removed caller_number from phone field, always uses `+441234567{run_id:05d}` (same as old working polling script).
  3. **Missing `turns` variable**: `_parse_turns()` was never called. Fix: added `turns = _parse_turns(transcript_text)`.
  4. **Transcript format mismatch**: `_parse_turns` checked for lines starting with `user:` but real transcript format is `[timestamp] user: text`. Fix: strip `[timestamp]` prefix before parsing.
  5. **Async message send**: Used `run_in_executor` which failed when event loop was shutting down. Fix: made message send synchronous via `_cw_api()`.
- **Duration fix**: Added `_start_time = time.time()` at pipeline start, changed `"call_duration_seconds": None` to `int(time.time() - _start_time)`.
- Verified: test run 4444 created Chatwoot conversation 91 with full transcript.

#### 68. docker-compose-aios.yml — Cleaned & Fixed ✅
- Removed nested 3-way merge conflict (`<<<<<<< HEAD` x2, `=======`, `>>>>>>>`)
- Removed duplicate `EXT_2000_SECRET` from asterisk env (was 3 copies)
- Removed stale `ari_manager.py` volume mount (pointed to outdated file)
- Added `run_pipeline.py` + `chatwoot_sync.py` volume mounts
- Added `aios-foss` network to dograh-api service
- Added `EXT_2000_SECRET=2000pass` to `.env.aios` (silenced warning)
- All validated: `docker compose config` passes

#### 69. Emma v3 Prompt — Deployed (7,255 chars) ✅
- Completely rewritten from v2 (6,691 chars) with:
  - **Adaptive LOD**: 3 modes — Brief (fast facts), Standard (conversation), Narrative (rich descriptions). Emma reads the customer's pace within 10 seconds.
  - **Emotional radar**: Detects stressed/excited/confused/nervous/hesitant/sad and adapts naturally.
  - **Proactive intelligence**: Connects dots before customer asks (Umrah + elderly parents → wheelchair assistance; Lahore → ask which area)
  - **Deeper cultural identity**: British-Pakistani voice with natural Urdu mix, understanding of community needs
  - **Stronger anti-pattern rules**: Never ask two questions at once, never say "I understand your concern"
- Deployed to workflow_definitions Node 1 (Travel Sales Conversation)

#### 70. Emma Taylor TTS Voice — Switched ✅
- From: `pFZP5JQG7iQjIQuC4Bku` (Lily - Velvety Actress)
- To: `S9EGwlCtMF7VXtENq79v` (Emma Taylor - Gentle, London accent)
- Updated in `user_configurations` DB

#### 71. Standalone Emma Chat URL ✅
- URL: `http://10.0.0.100:8081/` (LAN) or `https://voice.socialbeesai.com/chat` (public via Traefik with stripPrefix)
- Dark-themed chat UI with BASE path detection for Traefik proxy
- Uses v3 prompt (same as voice calls)
- API: `X-API-Key: dgr_JxFoGXkzncAlJM2aUhPhFOZ_GCQKgBHpajfgH15V0Bc`

#### 72. Text Chat Knowledge Injection — Fixed ✅
- **Problem**: Dograh's text chat runner doesn't pass the full workflow node prompt to the LLM (unlike voice pipeline which uses the complete 7,255-char prompt)
- **Impact**: Text chat ignored company info — address, destinations, pricing all missing
- **Fix**: Modified `chat_server.py` to inject a knowledge message into every new text chat session after creation. `KNOWLEDGE_MSG` contains: address (123 High Street, London, E1 1AA), destinations, pricing, Umrah details
- All three services now give consistent answers: voice call, text chat API, and chat URL

#### 73. Shin Travels Address — Fixed ✅
- **Problem**: Missing from prompt entirely. Emma hallucinated "123 Adventure Lane" etc.
- **Website**: `shintravels.co.uk` — 123 High Street, London, E1 1AA
- **Fix**: Added to company info section in v3 prompt. Also injected into chat server knowledge message.
- Voice call: correct address. Text chat: correct address (via injection).

#### 74. Git — Cleaned & Pushed ✅
- Merge conflict markers removed from all files
- Temp files cleaned
- `docs/CHECKPOINT.md` stale copy deleted
- All 8 commits pushed to GitHub: `f111431` → `2f65ebe` → `0331202` → `d5081bb` → `3c6bbd6` → `e0edbf6` → `6cf77a3` → `9ca6faf`
- Server and dev PC in sync

### Key Files
| File | Purpose |
|------|---------|
| `/aios/dograh-patches/chatwoot_sync.py` | Real-time Chatwoot transcript sync (all bugs fixed) |
| `/aios/dograh-patches/run_pipeline.py` | Patched pipeline with sync hook + duration tracking |
| `/aios/dograh-patches/emma_v3_prompt.txt` | Emma v3 prompt (7,255 chars, adaptive LOD, address fixed) |
| `/aios/dograh-patches/chat_server.py` | Emma chat HTTP server with knowledge injection |
| `/aios/chat/index.html` | Emma chat UI with BASE path detection |
| `/aios/configs/traefik/dynamic/emma-chat.yml` | Traefik route with stripPrefix |
| `/aios/docker-compose-aios.yml` | Fixed merge conflicts, networks, volumes |
| `/aios/.env.aios` | EXT_2000_SECRET added |

### Running Services (End of Session 11)
| Service | URL/Port | Status |
|---------|----------|--------|
| Voice Call (Ext 102) | Dial 102 from any SIP phone | ✅ Emma v3 prompt, correct address, Emma Taylor voice |
| Text Chat | `https://voice.socialbeesai.com/chat` | ✅ Knowledge injected, correct answers |
| Chatwoot | `https://chatwoot.socialbeesai.com` | ✅ Transcripts syncing after every call |
| Dograh API | 10.50.0.30:8000 | ✅ Healthy, 4 networks (Voice/AI/Data/FOSS) |

### Known Issues
- Chat server runs in screen session (not Docker) — doesn't survive reboot without manual restart
- Dograh text chat runner doesn't pass full node prompt to LLM (knowledge injection via chat server is the workaround)
- OpenRouter balance — needs monitoring

### Next Steps
- Add chat server to docker-compose for reboot persistence
- Monitor Chatwoot sync for edge cases
- Native Urdu TTS voice cloning
- Fix Ext 105 Urdu pronunciation (LLM outputting English instead of Roman Urdu)

---

## Session 15 — June 23, 2026: Ext 105 Urdu TTS Troubleshooting + Ext 500 Test Setup

### Summary
Extensive debugging of Urdu pronunciation issues on Ext 105. User confirmed UpliftAI voice `helpdesk-agent` produces perfect Urdu on other systems, but through the pipeline zero Urdu was heard. Root cause was likely a combination of:
1. **Sample rate**: `TARGET_SAMPLE_RATE=8000` (monster voice fixed) but ffmpeg resampling (22050→8000) degrades Urdu consonant quality
2. **Prompt**: Nastaliq Urdu script instruction caused LLM to output English rejections ("I'm sorry, but I can...")
3. **Audio pipeline**: PCM_22050_16 → ffmpeg → 8000Hz introduces artifacts; replaced with ULAW_8000_8 direct from UpliftAI (native 8kHz mu-law, no ffmpeg)

### Changes Made

**tts-router server.py:**
- Added ULAW-based PCM path: requests `ULAW_8000_8` from UpliftAI, decodes mu-law to 16-bit PCM at 8kHz
- No ffmpeg resampling needed for UpliftAI PCM path (native 8kHz from API)
- Falls back to ffmpeg only when speed != 1.0 (atempo)
- UpliftAI's internal 22050→8000 conversion is higher quality than ffmpeg swresample

**docker-compose-aios.yml:**
- `UPLIFTAI_VOICE_ID: helpdesk-agent` (user confirmed working)
- `TARGET_SAMPLE_RATE: 8000` (prevents monster voice from 24000Hz mismatch)

**Bifrost config.yaml:**
- Removed custom `urdu` model (was pointing to Qwen)
- Restored original `multilingual` (Gemma) as primary
- Restored original fallback chains

**Prompt (update_imperium_prompt.py):**
- Reverted from Nastaliq script instruction to Roman Urdu
- Added stronger "YOU MUST SPEAK URDU" directive
- Restored original Roman Urdu examples

**Database:**
- Ext 105 workflow model reverted from `urdu` to `multilingual`
- `agent_triggers` restored for 102, 105, 500
- Ext 500 (Quick Urdu Test) workflow created (id=5)

**New Extension 500:**
- Clean test extension with no wiki, no complex prompt
- Greeting: "Assalam-o-Alaikum! Yeh test Urdu call hai. Aap kaisay hain?"
- Simple Roman Urdu prompt
- LLM: Bifrost `general-reasoning` (Gemma 4 free)
- TTS: UpliftAI `helpdesk-agent` via ULAW
- STT: Deepgram Urdu
- Dialplan: `exten => 500,1,Stasis(dograh)`
- Phone mapping: `telephony_phone_numbers` entry for 500 → workflow 5

### Current State
| Service | Status |
|---------|--------|
| Ext 500 (Test Urdu) | Dial 500 from any SIP phone |
| Ext 105 (Imperium/Zara) | Pronunciation still needs fixing (LLM output issue) |
| Ext 102 (SHIN/Emma) | Should be unaffected |
| tts-router (ULAW) | v4.2.0, returning audio/L16;rate=8000;channels=1 via ULAW path |
| Bifrost | Restarted, stock config |
| Dograh API | Restarted, agent_triggers restored |
| Asterisk | Dialplan reloaded with ext 500 |

### Files Changed
| File | Changes |
|------|---------|
| `configs/tts-router/server.py` | ULAW-based PCM path, no ffmpeg for UpliftAI |
| `docker-compose-aios.yml` | helpdesk-agent voice, TARGET_SAMPLE_RATE=8000 |
| `configs/bifrost/config.yaml` | Reverted to original (removed urdu model) |
| `configs/asterisk/extensions.conf` | Added ext 500 |
| `update_imperium_prompt.py` | Reverted to Roman Urdu + stronger Urdu directive |
| `CHECKPOINT.md` | Updated |

### Key Files Reference
| File | Purpose |
|------|---------|
| `/aios/configs/tts-router/server.py` | TTS router v4.2.0 with ULAW PCM path |
| `/aios/docker-compose-aios.yml` | Service definitions, env vars |
| `/aios/configs/bifrost/config.yaml` | Bifrost model routing |
| `/aios/update_imperium_prompt.py` | Ext 105 prompt updater |
| `/aios/configs/asterisk/extensions.conf` | Dialplan with ext 500 |
(End of file)
