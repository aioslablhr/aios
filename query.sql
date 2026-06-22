SELECT id, name, workflow_configurations->>'system_prompt' AS prompt_snippet,
       workflow_configurations->>'company' AS company,
       workflow_configurations->>'stt_engine' AS stt,
       workflow_configurations->>'tts_engine' AS tts
FROM workflow_definitions WHERE id IN (1, 3);
