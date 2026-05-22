# AIOS — Security & Credential Management
## Where secrets live, how they're injected, and how to rotate them

---

## 1. CREDENTIAL CLASSIFICATION

| Level | Location | Git-tracked | Examples |
|-------|----------|-------------|---------|
| **L1** | `.env` | **No** (gitignored) | Server passwords, API keys, extension secrets |
| **L2** | Config files as `${VAR}` | Yes — no real values | `pjsip.conf`, `ari.conf` |
| **L3** | Vault (future) | No | Planned migration target for all L1 secrets |

### NEVER
- Hardcode passwords in config files that are tracked in git
- Share `.env` via email, chat, or any unencrypted channel
- Commit `.env` or any file containing real secrets

---

## 2. CURRENT CREDENTIAL INVENTORY

### Asterisk (Voice Layer)
| Credential | Location | Value | Rotation |
|-----------|----------|-------|----------|
| Ext 100 secret | `.env` → `EXT_100_SECRET` | See `.env` | Manual — update env + restart |
| Ext 101 secret | `.env` → `EXT_101_SECRET` | See `.env` | Manual — update env + restart |
| Ext 102 secret | `.env` → `EXT_102_SECRET` | See `.env` | Manual — update env + restart |
| ARI admin password | `.env` → `ARI_ADMIN_PASSWORD` | See `.env` | Manual — update env + restart |
| SIP trunk password | `.env` (planned) | Not yet configured | N/A |

### Infrastructure
| Credential | Location | Value | Rotation |
|-----------|----------|-------|----------|
| Server sudo | `.env` → `SERVER_PASS` | See `.env` | Manual |
| Cloudflare API | `.env` → `CLOUDFLARE_API_KEY` | See `.env` | Via Cloudflare dashboard |
| CrowdSec API | `.env` → `CROWDSEC_API_KEY` | See `.env` | Via CrowdSec console |

### Cloud LLM APIs (not yet configured — all `<from Vault>`)
| Credential | Status |
|-----------|--------|
| Anthropic, OpenAI, Google, OpenRouter | Marked `<from Vault>` — Vault uninitialized |
| Deepgram, ElevenLabs, Retell | Marked `<from Vault>` — Vault uninitialized |
| WhatsApp token | Marked `<from Vault>` — Vault uninitialized |

---

## 3. THE ENVSUBST PATTERN

This is how secrets reach containers without leaking to git:

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

### Rotate a cloud API key
```bash
# 1. Revoke old key in cloud provider dashboard
# 2. Generate new key in cloud provider dashboard
# 3. Update .env on server
nano /aios/.env

# 4. Restart affected services
docker compose -f docker-compose-aios.yml up -d <service>

# 5. Verify integration works
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
```

### Secret scanning
GitHub Actions CI pipeline includes Trivy secret scan on every push.
If it catches a secret:
1. **Revoke the leaked credential immediately**
2. Rotate to a new value
3. Force-push is prohibited — use `git revert` or `git reset` + new commit
4. Verify the scan passes on next push

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

## 6. VAULT STRATEGY (future)

Vault container is running at `10.20.0.50` but **uninitialized**.

### When Vault is operational
1. All L1 secrets migrate from `.env` to Vault KV store
2. Services authenticate via Vault Agent sidecar or AppRole
3. `.env` shrinks to contain only Vault address + AppRole credentials
4. Vault is backed up to MinIO encrypted

### Migration order
1. Asterisk extension secrets (lowest risk — internal only)
2. Cloud API keys (highest risk — rotate first)
3. Server credentials (root-level access)

---

*Created May 21, 2026 — AIOS Security & Credential Management*
