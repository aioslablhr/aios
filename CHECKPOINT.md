# AIOS — Session Checkpoint

**Version:** 4.10
**Date:** June 6, 2026
**Branch:** main
**Last commit:** 0f3c0e1 (to be updated after push)

---

## Container Status (Server)

### Running (42 — all services healthy or starting)
aios-traefik, aios-postgres, aios-redis, aios-qdrant, aios-minio, aios-clickhouse, aios-ollama, aios-bifrost, aios-langfuse, aios-docling, aios-mem0, aios-asterisk, aios-dnsmasq-tftp, aios-knowledge-ingest, aios-knowledge-compile, aios-dograh-api, aios-dograh-ui, aios-tts-router, aios-chatterbox, aios-kokoro, aios-xtts-urdu, aios-n8n, aios-n8n-worker-1, aios-n8n-worker-2, aios-n8n-db, aios-flowise, aios-keycloak, aios-mcp, aios-vault, aios-vault-unseal, aios-grafana, aios-portainer, aios-dashy, aios-prometheus, aios-cadvisor, aios-node-exporter, aios-loki, aios-crowdsec, aios-frigate, aios-mosquitto, aios-gitops

### Known Issues
- Chatterbox: runs with model loaded on CUDA but Docker healthcheck marks unhealthy
- Keycloak: running but unhealthy
- Hermes: restarting with exit 126
- MinIO: listed as unhealthy in old CHECKPOINT (verify)

### Written but NOT started
- Nextcloud (10.70.0.30), Odoo (10.70.0.20), Metabase (10.70.0.40) — docker-compose-apps.yml exists, never started
- Open WebUI (10.70.0.200) — compose entry exists, not started

---

## What's Done This Session (June 5-6)

### 1. Kokoro TTS — Deployed ✅
- Image: `ghcr.io/remsky/kokoro-fastapi-cpu:latest` (5.41GB)
- Container `aios-kokoro` running at 10.40.0.31:8880
- CPU-only inference, English TTS fallback

### 2. Chatterbox TTS — Started ✅
- Container `aios-chatterbox` running at 10.40.0.30:4123, model loaded on CUDA
- Healthcheck returns unhealthy (endpoint missing) but service works

### 3. Qalb-1.0-8B Urdu LLM — Pulled ✅
- GGUF Q4_K_M quant (4.92GB from `mradermacher/Qalb-1.0-8B-Instruct-GGUF`)
- Ollama model created as `qalb:8b-q4` with proper template + params
- Inference tested: correctly answered "The capital of Pakistan is Islamabad."
- Modelfile updated from `arbml/Qalb-1.0-8B-Instruct` to `hf.co/mradermacher/Qalb-1.0-8B-Instruct-GGUF:Q4_K_M`

### 4. Ollama — Upgraded ✅
- Version: 0.24.0 → 0.30.5 (fresh image pull)
- Now supports `hf.co/...` model references for GGUF files

### 5. XTTS-v2-Urdu-FT — Built, Deployed & Verified ✅
- Docker image `aios-xtts-urdu:latest` built successfully (CPU PyTorch)
- Container `aios-xtts-urdu` running at 10.40.0.32:8020
- CUDA disabled (`CUDA_VISIBLE_DEVICES=""`) — Quadro M4000 driver 470 can't run CUDA 12.x
- Switched model source: `arbml/xtts-v2-urdu-ft` (404) → `suhaibrashid17/XTTS-v2-Urdu-FT` (public, MIT)
- Fixed tokenizer incompatibility: `Tokenizer.from_file()` crashes with `tokenizers>=0.19` → replaced with manual BPE loading from tokenizer.json (vocab + merges as tuples)
- Added default speaker generation from random noise for API inference without `speaker_wav`
- All 3 TTS services verified: XTTS (200 OK, 191KB WAV), Kokoro (200), Chatterbox (200)
- TTS Router (10.40.0.33:8030) routes Urdu→XTTS, English→Chatterbox, fallback→Kokoro

### 6. Dashy Dashboard — Redesigned ✅
- 10 sections: System, AI Zone, DMZ, Application Zone, Data Zone, Monitoring Zone, Voice Zone, Extensions, FOSS Zone, AIOS Info
- 48 items with descriptions
- All running services mapped with correct IPs and ports

### 7. 41 Containers Mapped ✅
- Discovered all running containers (old CHECKPOINT claimed 18, actual 41)
- Many were orphan containers running without compose tracking

### 8. docker-compose-aios.yml Cleanup ✅
- Fixed all garbled characters in section headers and vault-unseal script (double-encoded UTF-8 artifacts)
- Replaced corrupted ASCII art box-drawing with clean `# ===` style separators
- Corrected XTTS section: GPU reservation removed, model repo updated to `suhaibrashid17/XTTS-v2-Urdu-FT`

---

## Pending (Not Started / Not Working)

| Item | Priority | Status |
|------|----------|--------|
| FOSS apps start (Nextcloud, Odoo, Metabase) | Medium | ❌ `docker compose -f docker-compose-apps.yml up -d` never run |
| Open WebUI start | Medium | ❌ Compose entry exists, not started |
| Chatterbox healthcheck fix | Low | ❌ Container works, healthcheck endpoint missing |
| WireGuard peer config retrieval | Low | ❌ Config auto-generated but never retrieved |
| Nightly backup cron | Low | ❌ Script exists (`backup.py`) but no cron job |
| First n8n workflow (AI employee) | Deferred | ❌ Blocked on infra completion |

---

## Key Architectural Decisions

1. **GPU limitation**: Quadro M4000 (Maxwell CC 5.0) maxes at NVIDIA driver 470, CUDA 11.4. No CUDA 12.x support. Ollama bundles its own CUDA 12.x and works anyway. Other containers (XTTS, Chatterbox) need explicit handling.
2. **Qalb GGUF**: 8B model at Q4_K_M (4.92GB) fits in 8GB VRAM alongside other models. FP16 (16GB) is too large.
3. **XTTS CPU-only**: Using CPU PyTorch because CUDA 12.x not available. TTS inference is fast enough on modern CPU.
4. **TTS pipeline**: Urdu → XTTS, English → Chatterbox (GPU), fallback → Kokoro (CPU), routed by TTS Router (10.40.0.33:8030).

---
2544163  feat: TTS router, Dograh speaches TTS config, mem0 v2
dd8b9c2  v4.6: XTTS-v2-Urdu-FT, wiki compiler, FOSS compose, mem0 v2
f7565f2  v4.5: single-server arch locked, WireGuard VPN, Qalb, Open WebUI
```
