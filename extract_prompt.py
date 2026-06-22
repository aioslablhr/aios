"""Extract node-2 prompt from workflow JSON."""
import json, sys

with open('/tmp/wf3_cleaned.json') as f:
    d = json.load(f)

nodes = d.get('nodes', d.get('workflow', {}).get('nodes', []))
for n in nodes:
    if n.get('title') == 'Node 2' or n.get('id') == 'node-2':
        params = n.get('params', n.get('parameters', {}))
        prompt = params.get('prompt', params.get('message', ''))
        print(f"--- Node: {n.get('title', n.get('name', 'unknown'))} ---")
        print(f"Prompt length: {len(prompt)} chars")
        print(prompt[:3000])
        print("\n... (truncated)" if len(prompt) > 3000 else "")
        break
