#!/bin/bash
# AIOS Data Layer — Full Functional Test
# Run: bash /aios/scripts/test-data-layer.sh
# Tests EVERY data service end-to-end: Postgres, Qdrant, Redis, MinIO, ClickHouse, Mem0, Docling, Knowledge Pipeline

G='\033[92m' R='\033[91m' Y='\033[93m' C='\033[96m' B='\033[1m' N='\033[0m'
PASS=0 FAIL=0
pass() { echo -e "  ${G}✓${N} $1"; ((PASS++)); }
fail() { echo -e "  ${R}✘${N} $1"; ((FAIL++)); }
info() { echo -e "  ${C}→${N} $1"; }
header() { echo -e "\n${B}${C}══ $1 ═══════════════════════════════════${N}"; }

echo -e "${B}${C}══════════════════════════════════════════════════${N}"
echo -e "${B}${C}  AIOS Data Layer — Full Functional Test${N}"
echo -e "${B}${C}  $(date)${N}"
echo -e "${B}${C}══════════════════════════════════════════════════${N}"

# ─────────── 1. POSTGRES ───────────
header "POSTGRES (10.30.0.10)"

if docker exec aios-postgres psql -U aios -d aios -c 'SELECT 1' >/dev/null 2>&1; then
  pass "Connection — aios database"
else
  fail "Connection — aios database"
fi

DBS=$(docker exec aios-postgres psql -U aios -d postgres -t -c "SELECT datname FROM pg_database ORDER BY datname" 2>/dev/null | tr -d ' ')
EXPECTED_DBS="aios dograh keycloak langfuse litellm"
MISSING=0
for db in $EXPECTED_DBS; do
  echo "$DBS" | grep -q "$db" || { info "  Missing DB: $db"; ((MISSING++)); }
done
[ "$MISSING" -eq 0 ] && pass "Databases — aios, dograh, keycloak, langfuse, litellm" \
  || fail "Databases — missing $MISSING expected DBs"

PGVEC=$(docker exec aios-postgres psql -U aios -d aios -t -c "SELECT extname FROM pg_extension WHERE extname='vector'" 2>/dev/null | tr -d ' ')
[ "$PGVEC" = "vector" ] && pass "pgvector extension installed" || fail "pgvector extension missing"

docker exec aios-postgres psql -U aios -d aios -c "
  CREATE TABLE IF NOT EXISTS _test_employees (
    id SERIAL PRIMARY KEY, name TEXT, role TEXT, salary NUMERIC
  );
  INSERT INTO _test_employees (name, role, salary) VALUES ('Test User', 'Engineer', 75000);
  SELECT * FROM _test_employees;
  DROP TABLE _test_employees;" >/dev/null 2>&1 && pass "CRUD — create, insert, select, drop" \
  || fail "CRUD — table operations"

# ─────────── 2. QDRANT ───────────
header "QDRANT (10.30.0.20)"

QDRANT_OK=$(curl -s -o /dev/null -w '%{http_code}' -H 'api-key: aios_qdrant_2026' http://10.30.0.20:6333/collections 2>/dev/null)
[ "$QDRANT_OK" = "200" ] && pass "Connection — API responds" || fail "Connection — no response"

COLLECTIONS=$(curl -s -H 'api-key: aios_qdrant_2026' http://10.30.0.20:6333/collections 2>/dev/null)
echo "$COLLECTIONS" | grep -q "knowledge_chunks" && pass "Collection — knowledge_chunks exists" || fail "Collection — knowledge_chunks missing"

python3 /aios/scripts/_test_qdrant.py 2>/dev/null && pass "Qdrant — upsert + search works (768-dim)" || fail "Qdrant — functional test failed"

# Cleanup
curl -s -X POST -H 'api-key: aios_qdrant_2026' -H 'Content-Type: application/json' \
  http://10.30.0.20:6333/collections/knowledge_chunks/points/delete \
  -d '{"filter":{"must":[{"has_id":["a1b2c3d4"]}]}}' >/dev/null 2>&1

# ─────────── 3. REDIS ───────────
header "REDIS (10.30.0.30)"

PONG=$(docker exec aios-redis redis-cli PING 2>/dev/null)
[ "$PONG" = "PONG" ] && pass "PING — responds" || fail "PING — no response"

docker exec aios-redis redis-cli SET _test_key "hello_aios" >/dev/null 2>&1
GET_VAL=$(docker exec aios-redis redis-cli GET _test_key 2>/dev/null)
[ "$GET_VAL" = "hello_aios" ] && pass "SET/GET — read-write works" || fail "SET/GET — failed"

docker exec aios-redis redis-cli DEL _test_key >/dev/null 2>&1

# ─────────── 4. MINIO ───────────
header "MINIO (10.30.0.40 — S3 API) | Console (10.30.0.40:9001)"

MINIO_OK=$(curl -s -o /dev/null -w '%{http_code}' http://10.30.0.40:9000/minio/health/live 2>/dev/null)
[ "$MINIO_OK" = "200" ] && pass "S3 API Health — live" || fail "S3 API Health — not responding"

CONSOLE_OK=$(curl -s -o /dev/null -w '%{http_code}' http://10.30.0.40:9001 2>/dev/null)
[ "$CONSOLE_OK" = "200" ] && pass "Console UI — accessible" || fail "Console UI — not responding"

BUCKETS=$(docker exec aios-minio mc ls local/ 2>/dev/null | awk '{print $NF}')
for b in raw-uploads processed-text test-bucket voice-audio; do
  echo "$BUCKETS" | grep -q "$b" && pass "  Bucket — $b" || fail "  Bucket — $b missing"
done

echo "test_upload_ok" | docker exec -i aios-minio mc pipe local/raw-uploads/_test_ping.txt >/dev/null 2>&1
DOWNLOAD=$(docker exec aios-minio mc cat local/raw-uploads/_test_ping.txt 2>/dev/null)
[ "$DOWNLOAD" = "test_upload_ok" ] && pass "Upload/Download — content preserved" || fail "Upload/Download — corrupted"

# ─────────── 5. CLICKHOUSE ───────────
header "CLICKHOUSE (10.60.0.11)"

CH_OK=$(curl -s -o /dev/null -w '%{http_code}' http://10.60.0.11:8123/ping 2>/dev/null)
[ "$CH_OK" = "200" ] && pass "Ping — responds" || fail "Ping — no response"

CH_SEL=$(docker exec aios-clickhouse clickhouse-client -q "SELECT 1" 2>/dev/null)
[ "$CH_SEL" = "1" ] && pass "Query — SELECT 1 works" || fail "Query — failed"

docker exec aios-clickhouse clickhouse-client -q "
  CREATE TABLE IF NOT EXISTS _test_events (ts DateTime, event String, user_id UInt32)
  ENGINE = MergeTree() ORDER BY ts" 2>/dev/null
docker exec aios-clickhouse clickhouse-client -q "
  INSERT INTO _test_events VALUES (now(), 'test_event', 1)" 2>/dev/null
CH_TEST=$(docker exec aios-clickhouse clickhouse-client -q "SELECT count() FROM _test_events" 2>/dev/null | tr -d ' ')
[ "$CH_TEST" != "0" ] && pass "CRUD — insert + select works" || fail "CRUD — failed"
docker exec aios-clickhouse clickhouse-client -q "DROP TABLE _test_events" >/dev/null 2>&1

# ─────────── 6. MEM0 ───────────
header "MEM0 (10.20.0.50)"

MEM0=$(curl -s http://10.20.0.50:8000/health 2>/dev/null)
echo "$MEM0" | grep -q "deferred\|ok" && pass "Health — API running" || fail "Health — no response"

# ─────────── 7. DOCLING ───────────
header "DOCLING (10.20.0.60)"

DOC_HEALTH=$(curl -s http://10.20.0.60:8000/health 2>/dev/null)
echo "$DOC_HEALTH" | grep -q 'status.*ok' && pass "Health — parser ready" || fail "Health — degraded"

DOC_PARSE=$(curl -s -X POST http://10.20.0.60:8000/v1/parse -F 'file=@-;filename=test.txt' 2>/dev/null <<< 'AIOS payroll test: Employee #1001')
echo "$DOC_PARSE" | grep -q 'status.*ok' && pass "File Upload — parses text" || fail "File Upload — failed"

DOC_PARSE_MINIO=$(python3 -c "
import requests
r = requests.post('http://10.20.0.60:8000/v1/parse/minio', json={'bucket':'raw-uploads','key':'_test_ping.txt'}, timeout=15)
print(r.status_code, r.json().get('status'))
" 2>/dev/null)
echo "$DOC_PARSE_MINIO" | grep -q "200 ok" && pass "MinIO Parse — reads from S3" || fail "MinIO Parse — failed ($DOC_PARSE_MINIO)"

# ─────────── 8. KNOWLEDGE INGEST ───────────
header "KNOWLEDGE INGEST (10.20.0.55)"

docker logs aios-knowledge-ingest 2>&1 | grep -qi "watch" && pass "Daemon — running & watching raw-uploads every 30s" || fail "Daemon — not watching"

INGEST_LOG=$(docker logs aios-knowledge-ingest 2>&1 | grep -c "Processing")
[ "$INGEST_LOG" -gt 0 ] && pass "Ingestion — process_file triggered ($INGEST_LOG files)" || info "No new files since daemon started (expected if no uploads)"

# ─────────── 9. CROSS-SERVICE CONNECTIVITY ───────────
header "CROSS-SERVICE CONNECTIVITY"

# Docling → MinIO
DOC_ACCESS=$(python3 -c "
import requests
try:
  r = requests.post('http://10.20.0.60:8000/v1/parse/minio', json={'bucket':'raw-uploads','key':'_test_ping.txt'}, timeout=10)
  print('ok' if r.status_code == 200 and r.json().get('status') == 'ok' else 'fail')
except Exception as e: print(f'fail: {e}')
" 2>/dev/null)
echo "$DOC_ACCESS" | grep -q "ok" && pass "Docling → MinIO — S3 read works" || fail "Docling → MinIO — $DOC_ACCESS"

# Knowledge Ingest → Docling
INGEST_ACCESS=$(docker logs aios-knowledge-ingest 2>&1 | grep "Docling failed" | tail -1)
[ -z "$INGEST_ACCESS" ] && pass "Ingest → Docling — no parse errors" || fail "Ingest → Docling — $INGEST_ACCESS"

# Knowledge Ingest → Qdrant
INGEST_QDRANT=$(docker logs aios-knowledge-ingest 2>&1 | grep "Indexed\|Qdrant" | tail -1)
[ -z "$INGEST_QDRANT" ] && info "Ingest → Qdrant — no indexed points yet (needs Phase B)" || info "Ingest → Qdrant — $INGEST_QDRANT"

# Server → All Data Zone
for ip in 10.30.0.10 10.30.0.20 10.30.0.30 10.30.0.40; do
  ping -c1 -W2 "$ip" >/dev/null 2>&1 && pass "Network — $ip reachable" || fail "Network — $ip unreachable"
done

# ─────────── 10. DASHY UI ───────────
header "DASHY (10.60.0.70 — served via Traefik at socialbeesai.com)"

DASHY_DIRECT=$(curl -s -o /dev/null -w '%{http_code}' http://10.60.0.70:8080 2>/dev/null)
[ "$DASHY_DIRECT" = "200" ] && pass "Direct — http://10.60.0.70:8080 = $DASHY_DIRECT" || fail "Direct — not responding"

DASHY_PROXY=$(curl -s -o /dev/null -w '%{http_code}' http://10.10.0.10 2>/dev/null)
[ "$DASHY_PROXY" = "200" ] && pass "Via Traefik — http://10.10.0.10 = $DASHY_PROXY" || info "Via Traefik — expected if TLS redirects to HTTPS"

DASHY_IP=$(curl -s -o /dev/null -w '%{http_code}' http://10.0.0.100:8082 2>/dev/null)
[ "$DASHY_IP" = "200" ] && pass "Fallback — http://10.0.0.100:8082 = $DASHY_IP" || fail "Fallback — not accessible"

# ─────────── CLEANUP ───────────
header "CLEANUP"
docker exec aios-minio mc rm local/raw-uploads/_test_ping.txt >/dev/null 2>&1

# ─────────── SUMMARY ───────────
TOTAL=$((PASS+FAIL))
echo -e "\n${B}${C}══════════════════════════════════════════════════${N}"
echo -e "${B}Results:  ${G}${PASS} passed${N}  |  ${R}${FAIL} failed${N}  |  $TOTAL total${N}"
echo -e "${B}${C}══════════════════════════════════════════════════${N}"
[ "$FAIL" -gt 0 ] && echo -e "${YELLOW}  → Some tests failed. Scroll up for details.${N}" || echo -e "${G}  → Data layer fully operational.${N}"
exit $FAIL
