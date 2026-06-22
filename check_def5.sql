select id, workflow_id, is_current from workflow_definitions where id=5;
select workflow_json::json->'nodes'->'node-2'->'data'->>'prompt' as prompt_preview from workflow_definitions where id=5;
