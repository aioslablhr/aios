SELECT jsonb_pretty(workflow_json #> '{nodes,0}') FROM workflow_definitions WHERE id = 3;
