# AIOS — Standard Operating Procedures
## Dual-Layer Development: Build infrastructure once, deploy use cases on top

---

## 1. EVERY SESSION — Start & End

### Before starting work
```
1. Read CHECKPOINT.md       — know current state, known issues, next steps
2. Read INVENTORY.md         — verify IPs, ports, credentials are current
3. git pull                  — ensure Dev PC is current
4. git log --oneline -5      — know what was done last
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
1. Verify all containers healthy     — docker ps --format 'table {{.Names}}\t{{.Status}}'
2. Run ./scripts/test-all.sh         — verify all 16 public endpoints respond
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
  checkpoint: update for credential vaulting session
  traefik: fix route for bifrost — add aios-ai to networks
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
| Dev PC → Server | Git push (GitOps auto-deploy) | Default workflow — Dev PC edits → push → server |
| Server → Dev PC | Git pull | At session end to sync server-side changes |
| Both | Verify with `git log --oneline` | After every sync |

### Source of truth
**Dev PC** (`D:\AIOS`) is the primary editing environment and git client.
**GitHub** (`github.com/aioslablhr/aios`) is the remote.
**Server** (`/aios/`) deploys via GitOps — DO NOT edit directly on server unless testing.
If you must edit on server, `scp` back to Dev PC and handle merge conflicts via git.

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
docker inspect aios-asterisk --format '{{.State.Health.Status}}'
docker exec aios-asterisk asterisk -rx "core show version"
```

### Verify all public endpoints (from server)
```bash
./scripts/test-all.sh
```

### Check container count vs expected (34 services)
```bash
docker ps | wc -l
```

---

## 5. ADDING A NEW SERVICE

1. **Assign Docker network zone** — see INVENTORY.md: network zones table
2. **Allocate IP** — use next available in the zone's /24
3. **Add to docker-compose-aios.yml** — with healthcheck, volumes, networks
4. **Add secrets to .env** — follow envsubst pattern (see SECURITY.md)
5. **Create Traefik route** — add to configs/traefik/dynamic/aios.yml
6. **Add Dashy tile** — add to configs/dashy/conf.yml
7. **Update INVENTORY.md** — add to main services table
8. **Update CHECKPOINT.md** — current state section
9. **Update creds.sh** — if the service has credentials
10. **git add + commit + push**

---

## 6. ADDING AN ASTERISK EXTENSION

1. Generate password → add to `.env`
2. Add auth + endpoint + aor block in `pjsip.conf` with `${VAR}` password
3. Add dialplan entry in `extensions.conf`
4. Restart asterisk: `docker compose -f docker-compose-aios.yml up -d asterisk`
5. Test softphone registration
6. `git commit + push`

---

## 7. DISASTER RECOVERY (planned)
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

## 8. DEVELOPMENT PATTERNS

### Diagnose → Treat → Verify
Always in this order. Never skip a step.

```
FAIL → read logs → understand → one fix → test → PASS → next
                                              → FAIL → back to "understand"
```

### Error isolation
When a Docker service fails:
```
docker run --rm <image> <binary>  # bypass compose
→ binary works?  → compose/network problem
→ binary fails?  → image/entrypoint problem
→ image wrong?   → Dockerfile problem
```

### Network zone debugging
```
# Check if service is on correct network
docker inspect aios-<service> --format '{{json .NetworkSettings.Networks}}' | jq

# Test connectivity between zones
docker exec aios-traefik curl -s http://<target-ip>:<port>
```

---

*Updated May 26, 2026 — AIOS Standard Operating Procedures v4.2*
