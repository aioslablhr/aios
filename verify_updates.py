import subprocess, json

def psql(sql):
    cmd = [
        'docker', 'exec', '-e', 'PGPASSWORD=aios_secret_2026',
        'aios-postgres', 'psql', '-h', 'localhost', '-U', 'aios',
        '-d', 'dograh', '-t', '-A', '-c', sql
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return r.stdout.strip() if not r.returncode else None

# Verify definitions 3 and 4
for def_id in [3, 4]:
    result = psql(f"SELECT workflow_configurations::text FROM workflow_definitions WHERE id={def_id}")
    if result:
        cfg = json.loads(result)
        print(f"Def {def_id}: company={cfg.get('company', 'MISSING')}")
        print(f"  Keys: {list(cfg.keys())}")
