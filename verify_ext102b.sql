-- Extract prompt length from node-2
SELECT id,
  length(
    jsonb_extract_path_text(
      workflow_json::jsonb,
      'nodes'
    )::text
  ) as raw_len
FROM workflow_definitions WHERE id=3;
