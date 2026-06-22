#!/bin/bash
PGPASSWORD=aios_secret_2026
echo "=== Last LLM text from conversation ==="
docker exec -e PGPASSWORD=$PGPASSWORD aios-postgres psql -h localhost -U aios -d dograh -t -A -c "select text from workflow_run_text_sessions order by created_at desc limit 5;" 2>/dev/null
echo ""
echo "=== Workflow runs for ext 105 ==="
docker exec -e PGPASSWORD=$PGPASSWORD aios-postgres psql -h localhost -U aios -d dograh -t -A -c "select id, status, created_at from workflow_runs where definition_id=4 order by created_at desc limit 3;" 2>/dev/null
