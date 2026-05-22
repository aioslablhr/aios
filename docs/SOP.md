# AIOS — Standard Operating Procedures
## The development rhythm — never skip these steps

---

## 1. EVERY SESSION — Start & End

### Before starting work
```
1. Read CHECKPOINT.md        — know current state, known issues, next steps
2. Read SECURITY.md           — refresh credential locations
3. git pull                   — ensure Dev PC is current (if git-connected)
4. Verify running containers  — ssh ai@10.0.0.100 "docker ps"
5. Check git log --oneline -5 — know what was done last
```

### Every time you make a change
```
1. Diagnose first    — read logs, understand root cause
2. One change        — modify exactly ONE variable between tests
3. Test locally      — verify before proceeding
4. Update CHECKPOINT — record what changed and why
5. Git add + commit  — descriptive message, one concern per commit
6. Git push          — triggers GitOps auto-deploy
```

### Every time you finish a session
```
1. Verify all containers healthy     — docker ps --format '{{.Names}} {{.Status}}'
2. Sync Dev PC from server           — scp or git pull
3. Update CHECKPOINT.md              — current state, next steps, new known issues
4. git add + commit + push CHECKPOINT.md and any file changes
5. Verify push succeeded             — check GitHub Actions CI (if applicable)
```

---

## 2. GIT WORKFLOW

### Branching
| Branch | Purpose | Auto-deploy |
|--------|---------|-------------|
| `main` | Production — always deployable | Yes — GitOps polls every 30s |
| `dev` | Staging — test here first | No |
| `feature/*` | New capabilities | No |

### Commit message format
```
<area>: <action> — <reason>

Examples:
  asterisk: compile from source — Stasis init crash in apt package
  credentials: move secrets to .env via envsubst — configs leaked on public repo
  checkpoint: update for credential vaulting session
```

### Rules
- **Never commit secrets** — `.env` is gitignored, configs use `${VAR}` placeholders
- **Never commit without testing** — verify the container starts healthy
- **One concern per commit** — don't mix checkpoint updates with code changes
- **Always push before ending session** — GitOps deploys from `main`

---

## 3. FILE SYNC — Dev PC ↔ Server

| Direction | Method | When |
|-----------|--------|------|
| Dev PC → Server | `scp` from D:\AIOS to /aios | After editing on Dev PC |
| Server → Dev PC | `scp` from /aios to D:\AIOS | At session end, or when editing on server |
| Both | Verify checksums match | After every sync |

### Verify sync
```powershell
# Dev PC
Get-FileHash -Algorithm MD5 "D:\AIOS\<file>" | Select-Object Hash

# Server (run via ssh)
ssh ai@10.0.0.100 "md5sum /aios/<file>"
```

### Source of truth
The **server's git repo** (`/aios/`) is the source of truth.
GitHub (`github.com/aioslablhr/aios`) is the remote.
Dev PC (`D:\AIOS`) is a working copy — sync from server at session end.

---

## 4. CONTAINER OPERATIONS

### Rebuild a single service
```bash
docker compose -f docker-compose-aios.yml build --no-cache <service>
docker compose -f docker-compose-aios.yml up -d <service>
```

### View logs
```bash
docker logs aios-asterisk --tail 50
docker compose -f docker-compose-aios.yml logs asterisk
```

### Enter a running container
```bash
docker exec -it aios-asterisk bash
```

### Check health
```bash
docker inspect aios-asterisk --format '{{.State.Health.Status}}
docker exec aios-asterisk asterisk -rx "core show version"
```

---

## 5. ADDING A NEW SERVICE

1. **Assign Docker network zone** — see CLAUDE.md: network zones table
2. **Allocate IP** — use next available in the zone's /24
3. **Add to docker-compose-aios.yml** — with healthcheck, volumes, networks
4. **Add secrets to .env** — follow envsubst pattern (see SECURITY.md)
5. **Create entrypoint script** — if the service needs envsubst for configs
6. **Update PROJECT.md** — only if architecture changes (rare)
7. **Update CHECKPOINT.md** — current state section
8. **git add + commit + push**

---

## 6. ADDING AN ASTERISK EXTENSION

1. Generate password → add to `.env`
2. Add auth + endpoint + aor block in `pjsip.conf` with `${VAR}` password
3. Add dialplan entry in `extensions.conf`
4. Restart asterisk: `docker compose -f docker-compose-aios.yml up -d asterisk`
5. Test softphone registration
6. `git commit + push`

---

## 7. NEW CLIENT ONBOARDING (planned)
When `new-client.py` is complete, it will automate:
```
python3 /aios/scripts/new-client.py \
  --client-id <id> \
  --industry <type> \
  --language <lang> \
  --model <model> \
  --budget <usd> \
  --agent-name <name> \
  --whatsapp <number>
```

Until then: manual Keycloak org + Qdrant collection + Supabase schema + Bifrost key.

---

## 8. DISASTER RECOVERY (planned)
When `disaster-recovery.py` is complete:
```
python3 /aios/scripts/disaster-recovery.py --restore <backup-file>
```

Until then:
```
git clone git@github.com:aioslablhr/aios.git /aios
# Restore .env from backup (NOT in git)
docker compose -f docker-compose-aios.yml up -d
```

---

## 9. DEVELOPMENT PATTERNS

### Diagnose → Treat → Verify
Always in this order. Never skip a step.

```
FAIL → read logs → understand → one fix → test → PASS → next
                                              → FAIL → back to "understand"
```

### Error isolation (Principle 3)
When a Docker service fails:
```
docker run --rm <image> <binary>  # bypass compose
→ binary works?  → compose/network problem
→ binary fails?  → image/entrypoint problem
→ image wrong?   → Dockerfile problem
```

---

*Created May 21, 2026 — AIOS Standard Operating Procedures*
