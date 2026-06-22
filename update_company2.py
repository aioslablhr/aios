import json, psycopg2

conn = psycopg2.connect(host='10.30.0.10', user='aios', password='aios_secret_2026', dbname='dograh')
cur = conn.cursor()

for def_id, company in [(4, 'imperium'), (3, 'shin-travels')]:
    cur.execute("SELECT workflow_configurations::text FROM workflow_definitions WHERE id=%s", (def_id,))
    row = cur.fetchone()
    raw = row[0]
    cfg = json.loads(raw) if isinstance(raw, str) else (raw if raw else {})
    cfg['company'] = company
    cur.execute("UPDATE workflow_definitions SET workflow_configurations=%s WHERE id=%s", (json.dumps(cfg), def_id))
    print(f"  Updated def {def_id}: company={company}")

conn.commit()
cur.close()
conn.close()
print("Done")
