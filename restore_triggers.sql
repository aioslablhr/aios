INSERT INTO agent_triggers (trigger_path, workflow_id, organization_id, state) VALUES
('102', 1, 1, 'active'),
('105', 3, 1, 'active'),
('500', 5, 1, 'active')
ON CONFLICT (trigger_path) DO UPDATE SET workflow_id=EXCLUDED.workflow_id, state='active';
