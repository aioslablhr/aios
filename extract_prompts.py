import json, psycopg2
conn = psycopg2.connect(host='10.30.0.10', user='aios', password='aios_secret_2026', dbname='dograh')
cur = conn.cursor()

# Get workflow_json for def 4 (Ext 105)
cur.execute("SELECT workflow_json::text FROM workflow_definitions WHERE id=4")
row = cur.fetchone()
wj = json.loads(row[0])

# Find the agent node with the prompt
nodes = wj.get('nodes', [])
for node in nodes:
    node_type = node.get('type', '') or node.get('data', {}).get('type', '')
    node_id = node.get('id', '')
    prompt = node.get('data', {}).get('prompt', '')
    
    if prompt:
        preview = prompt[:200].replace('\n', '\\n')
        print(f"Node: {node_id}, Type: {node_type}")
        print(f"  Prompt ({len(prompt)} chars): {preview}")
        print(f"  Data keys: {list(node.get('data', {}).keys())}")
        print()

cur.close()
conn.close()
