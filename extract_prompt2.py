"""Clean wf3.json and extract prompt."""
import json

with open('/tmp/wf3.json') as f:
    raw = f.read().strip()
    d = json.loads(raw)

with open('/tmp/wf3_cleaned.json', 'w') as f:
    json.dump(d, f)

nodes = d.get('nodes', d.get('workflow', {}).get('nodes', []))
for n in nodes:
    if n.get('title') == 'Node 2' or n.get('id') == 'node-2':
        params = n.get('params', n.get('parameters', {}))
        prompt = params.get('prompt', params.get('message', ''))
        print(f"--- Node: {n.get('title', n.get('name', 'unknown'))} ---")
        print(f"Prompt length: {len(prompt)} chars")
        print(prompt[:3000])
        break
