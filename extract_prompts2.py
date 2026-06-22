import json, subprocess, sys

def psql(sql):
    cmd = [
        'docker', 'exec', '-e', 'PGPASSWORD=aios_secret_2026',
        'aios-postgres', 'psql', '-h', 'localhost', '-U', 'aios',
        '-d', 'dograh', '-t', '-A', '-c', sql
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if r.returncode:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return None
    return r.stdout.strip()

# Get workflow_json for def 4
result = psql("SELECT workflow_json::text FROM workflow_definitions WHERE id=4")
if not result:
    sys.exit(1)

wj = json.loads(result)
nodes = wj.get('nodes', [])
for node in nodes:
    data = node.get('data', {})
    prompt = data.get('prompt', '')
    node_type = data.get('type', node.get('type', ''))
    if prompt:
        preview = prompt[:300].replace('\n', '\\n')
        print(f"Node: {node.get('id')}, Type: {node_type}")
        print(f"  Prompt ({len(prompt)} chars): {preview}")
        print(f"  Data keys: {list(data.keys())}")
        print()
