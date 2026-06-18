SELECT initial_context FROM workflow_runs WHERE id = (SELECT max(id) FROM workflow_runs) AND mode = 'textchat';
