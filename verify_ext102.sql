SELECT id, pg_column_size(workflow_json) as json_size, workflow_configurations FROM workflow_definitions WHERE id=3;
