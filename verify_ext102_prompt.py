"""Fetch workflow from DB and verify node-2 prompt."""
import json, subprocess

# Re-fetch from DB
result = subprocess.run(
    ['docker', 'exec', '-i', 'aios-postgres', 'psql', '-U', 'aios', '-d', 'dograh', '-t', '-A', 
     '-c', 'SELECT workflow_json FROM workflow_definitions WHERE id=3;'],
    capture_output=True, text=True
)
raw = result.stdout.strip()
wf = json.loads(raw)

for n in wf['nodes']:
    if n['id'] == 'node-2':
        prompt = n['data']['prompt']
        print(f"node-2 prompt length: {len(prompt)} chars")
        print(f"First 200 chars: {prompt[:200]}")
        print(f"Contains {{wiki_content}}: {'{{wiki_content}}' in prompt}")
        print(f"Contains Zayn: {'Zayn' in prompt}")
        print(f"Contains SHIN Travels: {'SHIN Travels' in prompt}")
        print(f"Contains 14.: {'14.' in prompt}")  # Dograh guideline 14
        break
