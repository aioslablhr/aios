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

result = psql("SELECT jsonb_pretty(workflow_json::jsonb) FROM workflow_definitions WHERE id=4")
if result:
    print(result[:5000])
