#!/bin/bash
PGPASSWORD=aios_secret_2026
echo "Current model:"
docker exec -e PGPASSWORD=$PGPASSWORD aios-postgres psql -h localhost -U aios -d dograh -t -A -c "select workflow_configurations::json->'model_overrides'->'llm'->>'model' from workflow_definitions where id=4;"
echo "Reverting to multilingual..."
docker exec -e PGPASSWORD=$PGPASSWORD aios-postgres psql -h localhost -U aios -d dograh -c "
UPDATE workflow_definitions 
SET workflow_configurations = jsonb_set(
    workflow_configurations::jsonb,
    '{model_overrides,llm,model}',
    '\"multilingual\"'
)
WHERE id=4;
"
echo "Verified:"
docker exec -e PGPASSWORD=$PGPASSWORD aios-postgres psql -h localhost -U aios -d dograh -t -A -c "select workflow_configurations::json->'model_overrides'->'llm'->>'model' from workflow_definitions where id=4;"
