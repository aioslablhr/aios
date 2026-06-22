import json, psycopg2

conn = psycopg2.connect(host='10.30.0.10', user='aios', password='aios_secret_2026', dbname='dograh')
cur = conn.cursor()

# Update definition 4 (Ext 105 - Urdu Agent → Imperium)
cur.execute("SELECT workflow_configurations FROM workflow_definitions WHERE id=4")
row = cur.fetchone()
cfg = row[0] if isinstance(row[0], dict) else json.loads(row[0])
cfg['company'] = 'imperium'
cur.execute("UPDATE workflow_definitions SET workflow_configurations=%s WHERE id=4", (json.dumps(cfg),))

# Update definition 3 (Ext 102 - SHIN Travels)
cur.execute("SELECT workflow_configurations FROM workflow_definitions WHERE id=3")
row = cur.fetchone()
cfg = row[0] if isinstance(row[0], dict) else json.loads(row[0])
cfg['company'] = 'shin-travels'
cur.execute("UPDATE workflow_definitions SET workflow_configurations=%s WHERE id=3", (json.dumps(cfg),))

conn.commit()
cur.close()
conn.close()

print("Updated definitions 3 and 4 with company field")
