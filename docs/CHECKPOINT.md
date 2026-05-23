# AIOS — Session Checkpoint

## Current State: Phase 3 AI Core — Deployed (May 24, 2026)

### Running (15 containers healthy)
| Layer | Service | IP | Port | Status |
|-------|---------|----|------|--------|
| Data | PostgreSQL | 10.30.0.10 | 5432 | ✅ healthy |
| Data | Qdrant | 10.30.0.20 | 6333, 6334 | ✅ healthy |
| Data | Redis (orphan) | 10.30.0.30 | 6379 | ✅ healthy |
| Data | MinIO (orphan) | 10.30.0.40 | 9000, 9001 | ✅ healthy |
| AI | Ollama | 10.40.0.20 | 11434 | ✅ healthy — Mistral 7B, Qwen2.5 7B, Llama 3.2 3B |
| AI | Bifrost (LiteLLM) | 10.40.0.10 | 4000 | ✅ healthy — 6 models, Ollama + OpenRouter |
| Mon | ClickHouse | 10.60.0.11 | 8123, 9000 | ✅ healthy — Keeper mode |
| Mon | Langfuse | 10.60.0.10 | 3000 | ✅ live (no admin user created) |
| App | Keycloak (orphan) | 10.20.0.40 | 8080 | ✅ healthy |
| DMZ | Traefik (orphan) | 10.10.0.10 | 80, 443 | ✅ healthy |
| DMZ | CrowdSec (orphan) | 10.10.0.11 | 8080 | ✅ healthy |
| App | Vault | 10.0.0.100 | 8200 | ✅ unsealed |
| App | GitOps | 10.20.0.100 | — | ✅ polling GitHub every 30s |
| App | Hermes | 10.20.0.70 | — | ✅ running |
| Voice | Asterisk | 10.0.0.100 | 5060/udp, 8088 | ✅ healthy |
| Host | DNSmasq-TFTP | 10.0.0.100 | 69/udp | ✅ healthy |

### AI Pipeline Verified End-to-End
```
Bifrost (10.40.0.10:4000) → Ollama (10.40.0.20:11434) → Mistral 7B (GPU)
✅ Returns: "Hello there! How can I assist you today?" (26 tokens)
```

### LLM Routing
| Model | Backend | Provider | Status |
|-------|---------|----------|--------|
| mistral-7b | Ollama | ollama/mistral | ✅ verified |
| qwen-2.5-7b | Ollama | ollama/qwen2.5 | 🟡 pulled, untested |
| llama-3-8b | Ollama | ollama/llama3.2 (3.2B) | 🟡 pulled, untested |
| claude-4-sonnet | OpenRouter | openrouter/anthropic/... | 🔴 placeholder key |
| gemma-4 | OpenRouter | openrouter/google/... | 🔴 placeholder key |
| gpt-4o | OpenRouter | openrouter/openai/... | 🔴 placeholder key |

### Bifrost Config Notes
- Provider: `ollama/` prefix (not `openai/`) for local models
- Cache: disabled (Redis not deployed properly)
- Routing: `simple-shuffle` (not `usage-based-routing` — no Redis)
- Fallbacks: cross-configured between local and cloud models
- Port: `4000:4000` (0.0.0.0 binding, accessible from Dev PC)

### Next Steps
1. Deploy n8n (orchestration) — connect Langfuse + Bifrost + tools
2. Set up Cloudflare tunnel + DNS for public access
3. Create Langfuse admin user + first project
4. Generate Bifrost virtual keys for Langfuse logging
5. Pull Llama 3.1 8B in Ollama (replace 3.2 3B)
6. Set real OpenRouter API key for cloud model access
7. Wire Traefik → Bifrost route for `ai.socialbeesai.com/bifrost`

### Known Issues
- `llama-3-8b` model name serves `llama3.2:3b` (3.2B not 8B) — needs `llama3.1:8b` pull
- OpenRouter API key is placeholder `sk-or-v1-placeholder` — cloud models will 401
- No Langfuse admin user created yet — observability pipeline incomplete
- Redis, MinIO, Keycloak, Traefik, CrowdSec, Dashy orphan containers (not in compose)
- No TLS/SSL — Traefik not wired to Cloudflare tunnel
- `.env` gitignored — manual sync to server required
