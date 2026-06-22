UPDATE workflow_definitions
SET workflow_configurations = workflow_configurations::jsonb || '{"company": "imperium"}'::jsonb
WHERE id = 4;

UPDATE workflow_definitions
SET workflow_configurations = workflow_configurations::jsonb || '{"company": "shin-travels"}'::jsonb
WHERE id = 3;
