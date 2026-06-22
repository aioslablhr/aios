SELECT wfd.id, w.name, wfd.workflow_configurations->>'system_prompt' AS prompt_snippet,
       wfd.workflow_configurations->>'company' AS company,
       wfd.workflow_configurations->>'stt_engine' AS stt,
       wfd.workflow_configurations->>'tts_engine' AS tts,
       wfd.workflow_configurations->>'llm_model' AS llm
FROM workflow_definitions wfd
JOIN workflows w ON w.id = wfd.workflow_id
WHERE wfd.id IN (1, 3);
