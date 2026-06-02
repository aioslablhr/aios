# AIOS — Security & Credential Management
## Where secrets live, how they're injected, and how to rotate them

---

## 1. CREDENTIAL CLASSIFICATION

| Level | Location | Git-tracked | Examples |
|-------|----------|-------------|---------|
| **L1** | `.env` | **No** (gitignored) | Server passwords, API keys, extension secrets |
| **L2** | Config files as `${VAR}` | Yes — no real values | `pjsip.conf`, `ari.conf` |
| **L3** | Vault (active) | No | HashiCorp Vault at vault.socialbeesai.com — unsealed |

### NEVER
- Hardcode passwords in config files tracked in git
- Share `.env` via email, chat, or any unencrypted channel
- Commit `.env` or any file containing real secrets

---

## 2. CURRENT CREDENTIAL INVENTORY

### Infrastructure
| Credential | Location | Value | Rotation |
|-----------|----------|-------|----------|
| Server SSH | `.env` → `SERVER_PASS` | See `.env` | Manual |
| Cloudflare API | `.env` → `CLOUDFLARE_API_KEY` | See `.env` | Via Cloudflare dashboard |
| CrowdSec API | `.env` → `CROWDSEC_API_KEY` | See `.env` | Via CrowdSec console |

### Databases (Data Zone — 10.30.0.0/24)
| Credential | Location | Value | Rotation |
|-----------|----------|-------|----------|
| PostgreSQL | `.env` → `POSTGRES_PASSWORD` | aios_secret_2026 | Manual |
| Qdrant API key | `.env` → `QDRANT_API_KEY` | aios_qdrant_2026 | Manual |
| MinIO console | `.env` → `MINIO_ROOT_PASSWORD` | minioadmin | Manual |

### AI Gateway & LLM
| Credential | Location | Value | Rotation |
|-----------|----------|-------|----------|
| Bifrost admin key | `.env` → `BIFROST_ADMIN_KEY` | sk-aios-master-admin-key-change-me | Manual |
| OpenRouter API | `.env` → `OPENROUTER_API_KEY` | sk-or-v1-0855e04fc... | **REAL KEY SET May 26** |
| Anthropic API | `.env` (commented) | N/A | Not yet configured |
| OpenAI API | `.env` (commented) | N/A | Not yet configured |

### Workflow Automation (App Zone — 10.20.0.0/24)
| Credential | Location | Value | Rotation |
|-----------|----------|-------|----------|
| n8n DB password | `.env` → `N8N_DB_PASSWORD` | 21e8c7e99182e353a7326dff9b40d4ec | Manual |
| n8n encryption key | `.env` → `N8N_ENCRYPTION_KEY` | 32-char hex | Manual |

### Voice Layer (Voice Zone — 10.50.0.0/24)
| Credential | Location | Value | Rotation |
|-----------|----------|-------|----------|
| Ext 100 secret | `.env` → `EXT_100_SECRET` | See `.env` | Manual — update env + restart |
| Ext 101 secret | `.env` → `EXT_101_SECRET` | See `.env` | Manual — update env + restart |
| Ext 102 secret | `.env` → `EXT_102_SECRET` | See `.env` | Manual — update env + restart |
| Ext 103 secret | `.env` → `EXT_103_SECRET` | See `.env` | Manual |
| Ext 104 secret | `.env` → `EXT_104_SECRET` | See `.env` | Manual |
| Ext 9000 (Cisco) | `.env` → `EXT_9000_SECRET` | See `.env` | Manual |
| ARI admin password | `.env` → `ARI_ADMIN_PASSWORD` | 95vt3r6ke1w8lgqg6qpcui8e | Manual |
| Voicemail password | `voicemail.conf` (hardcoded) | 1234 | Manual |
| Dograh JWT secret | `.env` → `DOGRAH_JWT_SECRET` | aios-dograh-jwt-secret-2026 | Manual |
| SIP trunk password | `.env` (planned) | Not yet configured | N/A |

### Added Services (May 26)
| Credential | Location | Value | Notes |
|-----------|----------|-------|-------|
| Flowise admin | (first signup on web) | admin / admin | app.socialbeesai.com/flowise |
| MCP Server | — | — | No auth required (internal) |
| Dograh image | compose → `ghcr.io/dograh-hq/*` | OSS (was Docker Hub paid) | Apr 30 swap |

### Monitoring
| Credential | Location | Value | Rotation |
|-----------|----------|-------|----------|
| Grafana admin | `.env` → `GRAFANA_ADMIN_PASSWORD` | grafana_admin_2026 | Manual |
| Langfuse NextAuth | `.env` → `LANGFUSE_NEXTAUTH_SECRET` | Generated random base64 | Manual |
| Langfuse salt | `.env` → `LANGFUSE_SALT` | Generated random base64 | Manual |

### Vault
| Credential | Location | Value | Rotation |
|-----------|----------|-------|----------|
| Root token | `.vault-keys` (NOT in git) | (see .vault-keys on server) | Via Vault CLI |
| Unseal key 1 | `.vault-keys` (NOT in git) | (see .vault-keys on server) | Via Vault CLI |
| Unseal key 2–5 | `.vault-keys` (NOT in git) | (see .vault-keys on server) | Via Vault CLI |

### IP Phones & Cameras
| Credential | Location | Value | Rotation |
|-----------|----------|-------|----------|
| Cisco phone SIP pass | `SEP00270DC01C92.cnf.xml` | 9000pass (hardcoded in XML) | Manual |

### Cloud LLM APIs (not yet configured)
| Credential | Status |
|-----------|--------|
| Anthropic, OpenAI, Google | Not configured — commented in `.env` |
| Deepgram, ElevenLabs, Retell | Not needed — replaced by Whisper/Dograh/Chatterbox local GPU |
| WhatsApp token | Not configured — future notification channel |

---

## 3. THE ENVSUBST PATTERN

Secrets reach containers without leaking to git:

### How it works
```
.gitignore       .env (gitignored)          Git-tracked config     Container runtime
──────          ──────────────             ──────────────────     ────────────────
.env            EXT_100_SECRET=abc123      password=${EXT_100_SECRET}
                                                      │
                                                      ▼
                                            docker-compose injects env vars
                                                      │
                                                      ▼
                                            docker-entrypoint.sh runs envsubst
                                                      │
                                                      ▼
                                            /run/asterisk-configs/pjsip.conf
                                            password=abc123  ← real value, tmpfs only
```

### Required components per service
1. `.env` entry — the actual secret value (gitignored)
2. Config template — `${VAR_NAME}` placeholder (git-tracked)
3. `docker-compose` — `environment:` section maps `.env` → container
4. Entrypoint script — `envsubst` before starting the service
5. Runtime directory — substituted configs in `/run/` (tmpfs, not persisted to host)

### Entrypoint script template
```bash
#!/bin/bash
set -e
RUNTIME_CONF=/run/<service>-configs
mkdir -p "$RUNTIME_CONF"
cp /etc/<service>/*.conf "$RUNTIME_CONF/"
for f in "$RUNTIME_CONF"/*.conf; do
  envsubst < "$f" > "${f}.tmp" && mv "${f}.tmp" "$f"
done
exec <service-binary> <args>
```

### Docker-compose environment section
```yaml
environment:
  EXT_100_SECRET: ${EXT_100_SECRET}
  EXT_101_SECRET: ${EXT_101_SECRET}
```

---

## 4. CREDENTIAL ROTATION PROCEDURE

### Rotate an Asterisk extension password
```bash
# 1. Generate new password
# 2. Update .env on server
nano /aios/.env
# EXT_100_SECRET=new_password_here

# 3. Rebuild and restart asterisk
cd /aios
docker compose -f docker-compose-aios.yml up -d asterisk

# 4. Verify
docker exec aios-asterisk asterisk -rx "pjsip show endpoint 100"

# 5. Update softphone config with new password
# 6. Test registration
```

### Rotate any other credential
```bash
# 1. Update .env on server
# 2. Restart affected services
docker compose -f docker-compose-aios.yml up -d <service>
# 3. Verify the service works
```

---

## 5. GIT SECURITY

### .gitignore rules (already configured)
```
.env          — NEVER commit environment variables
.env.*        — NEVER commit any env file variants
*.key         — NEVER commit private keys
*.pem         — NEVER commit certificates
acme.json     — NEVER commit Let's Encrypt data (contains private keys)
data/         — Runtime data, bind mounts, volumes
.vault-keys   — Vault root token + unseal keys
```

### Push protection
GitHub push protection blocks secrets committed to git. `scripts/creds.sh` has secrets redacted — actual values reference ".env on server". Vault root token and Cloudflare API key removed from git-tracked creds.sh.

### What to do if a secret is committed
```bash
# 1. REVOKE the secret first (before anything else)
# 2. Rotate to a new value in .env
# 3. On server:
git log --oneline -5                  # find the bad commit
git revert <bad-commit>               # undo the commit
git push                              # clean history
```

---

## 6. VAULT STATUS

Vault is **running and unsealed** at `vault.socialbeesai.com` (host network on 10.0.0.100:8200). Currently stores root CA and internal PKI. Migration target for all L1 secrets from `.env`.

### When Vault is fully operational
1. All L1 secrets migrate from `.env` to Vault KV store
2. Services authenticate via Vault Agent sidecar or AppRole
3. `.env` shrinks to contain only Vault address + AppRole credentials
4. Vault is backed up to MinIO encrypted

### Migration order
1. Asterisk extension secrets (lowest risk — internal only)
2. Cloud API keys (highest risk — rotate first)
3. Server credentials (root-level access)

---

*Created May 21, 2026 • Updated May 26, 2026 — AIOS Security & Credential Management*
