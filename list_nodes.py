"""List nodes in Ext 102 workflow JSON."""
import sys, json

with open('/tmp/wf3.sqlout') as f:
    d = json.load(f)

nodes = d.get('nodes', [])
for n in nodes:
    data = n.get('data', {})
    name = data.get('name', n.get('title', '?'))
    nid = n.get('id', '?')
    prompt = data.get('prompt', '')
    print(f"{name} | {nid} | {len(prompt)} chars")
    if 'prompt' in data and len(prompt) > 100:
        print(f"  First 200: {prompt[:200]}")
    print()
