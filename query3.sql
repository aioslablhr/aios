SELECT wfd.id, w.name,
       wfd.workflow_configurations::text AS cfg_json
FROM workflow_definitions wfd
JOIN workflows w ON w.id = wfd.workflow_id
WHERE wfd.id IN (3, 4);
