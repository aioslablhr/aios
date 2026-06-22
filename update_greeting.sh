#!/bin/bash
PGPASSWORD=aios_secret_2026
docker exec -e PGPASSWORD=$PGPASSWORD aios-postgres psql -h localhost -U aios -d dograh -c "
UPDATE workflow_definitions 
SET workflow_json = jsonb_set(
    workflow_json::jsonb,
    '{nodes,node-1,data,greeting}',
    '\"السلام علیکم! امپیریم ڈویلپرز میں آپ کا خوش آمدید۔ میں زارا بول رہی ہوں۔ کیا میں آپ کی کسی چیز میں مدد کر سکتی ہوں؟\"'
)
WHERE id=4;
"
echo "=== Greeting updated ==="
docker exec -e PGPASSWORD=$PGPASSWORD aios-postgres psql -h localhost -U aios -d dograh -t -A -c "select workflow_json::json->'nodes'->'node-1'->'data'->>'greeting' from workflow_definitions where id=4;"
