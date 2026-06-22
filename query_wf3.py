import psycopg2, json
conn = psycopg2.connect(host='10.30.0.10', user='aios', password='aios_secret_2026', dbname='dograh')
cur = conn.cursor()
cur.execute("SELECT id, name, workflow_configurations FROM workflow_definitions WHERE id IN (1, 3)")
for row in cur.fetchall():
    wf_id, name, cfg_json = row
    cfg = cfg_json if isinstance(cfg_json, dict) else (json.loads(cfg_json) if cfg_json else {})
    print(f"ID: {wf_id}, Name: {name}")
    print(f"  Company: {cfg.get('company', 'NOT SET')}")
    sp = cfg.get('system_prompt', '')
    print(f"  System prompt ({len(sp)} chars): {sp[:300]}")
    print(f"  Keys: {list(cfg.keys())}")
    print()
cur.close()
conn.close()
