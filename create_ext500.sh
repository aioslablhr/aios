#!/bin/bash
set -e
PGPASSWORD=aios_secret_2026

cat > /tmp/create_ext500.sql << 'SQLEOF'
-- First create definition without workflow reference
INSERT INTO workflow_definitions (id, workflow_json, workflow_configurations, status, is_current)
VALUES (5, '{"nodes":{"node-1":{"type":"startCall","data":{"greeting":"السلام علیکم! یہ test Urdu call ہے۔ آپ کیسے ہیں؟","name":"startCall"}},"node-2":{"type":"llm","data":{"name":"Chat","prompt":"You are a friendly Urdu speaking assistant. Keep responses short. Always include Urdu words. CRITICAL: Write ALL Urdu words in proper Urdu (Nastaliq) script — for example آپ، کیسے، ہیں، جی، اچھا. NEVER write Urdu in Roman/English letters. Keep genuine English words (brand/technical) in ASCII English inside the Urdu sentence. The voice engine is native Urdu and only reads Urdu script correctly.\n\nCurrent conversation:\n{conversation}\n\nAssistant:","provider":"openrouter","model":"general-reasoning"}},"node-3":{"type":"endCall","data":{"prompt":"Say اللہ حافظ in Urdu (Nastaliq script).","name":"endCall"}}},"edges":[{"source":"node-1","target":"node-2"},{"source":"node-2","target":"node-3"}]}'::json, '{"company":"test","model_overrides":{"llm":{"model":"general-reasoning","api_key":"sk-aios-master-admin-key-change-me","base_url":"http://10.40.0.10:4000/v1","provider":"speaches"},"stt":{"model":"nova-3-general","api_key":"fe444a27a666a3e471b8002ff56be87f964b9938","language":"ur","provider":"deepgram"},"tts":{"model":"tts-1","voice":"uplift","api_key":"sk-placeholder","base_url":"http://aios-tts-router:8030/v1","provider":"openai"}},"max_call_duration":300}'::json, 'published', true)
ON CONFLICT (id) DO NOTHING;

-- Create workflow (released_definition_id can reference def 5 now)
INSERT INTO workflows (id, name, workflow_definition, organization_id, status, template_context_variables, call_disposition_codes, workflow_configurations, released_definition_id, workflow_uuid)
VALUES (5, 'Quick Urdu Test', '{"nodes":{"node-1":{"type":"startCall","data":{"greeting":"السلام علیکم! یہ test Urdu call ہے۔ آپ کیسے ہیں؟","name":"startCall"}},"node-2":{"type":"llm","data":{"name":"Chat","prompt":"You are a friendly Urdu speaking assistant. Keep responses short. Always include Urdu words. CRITICAL: Write ALL Urdu words in proper Urdu (Nastaliq) script — for example آپ، کیسے، ہیں، جی، اچھا. NEVER write Urdu in Roman/English letters. Keep genuine English words (brand/technical) in ASCII English inside the Urdu sentence. The voice engine is native Urdu and only reads Urdu script correctly.\n\nCurrent conversation:\n{conversation}\n\nAssistant:","provider":"openrouter","model":"general-reasoning"}},"node-3":{"type":"endCall","data":{"prompt":"Say اللہ حافظ in Urdu (Nastaliq script).","name":"endCall"}}},"edges":[{"source":"node-1","target":"node-2"},{"source":"node-2","target":"node-3"}]}'::json, 1, 'active', '{}'::json, '{}'::json, '{"company":"test","model_overrides":{"llm":{"model":"general-reasoning","api_key":"sk-aios-master-admin-key-change-me","base_url":"http://10.40.0.10:4000/v1","provider":"speaches"},"stt":{"model":"nova-3-general","api_key":"fe444a27a666a3e471b8002ff56be87f964b9938","language":"ur","provider":"deepgram"},"tts":{"model":"tts-1","voice":"uplift","api_key":"sk-placeholder","base_url":"http://aios-tts-router:8030/v1","provider":"openai"}},"max_call_duration":300}'::json, 5, '550e8400-e29b-41d4-a716-446655440000')
ON CONFLICT (id) DO UPDATE SET released_definition_id=5, workflow_definition=EXCLUDED.workflow_definition;

-- Link definition back to workflow
UPDATE workflow_definitions SET workflow_id=5 WHERE id=5;
SQLEOF

docker exec -i -e PGPASSWORD=$PGPASSWORD aios-postgres psql -h localhost -U aios -d dograh < /tmp/create_ext500.sql

echo "=== Done ==="
docker exec aios-asterisk asterisk -rx "dialplan reload" 2>/dev/null || true
echo "Dial 500 from any SIP phone to test"
