import subprocess

def psql(sql):
    cmd = [
        'docker', 'exec', '-e', 'PGPASSWORD=aios_secret_2026',
        'aios-postgres', 'psql', '-h', 'localhost', '-U', 'aios',
        '-d', 'dograh', '-t', '-A', '-c', sql
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return r.stdout.strip() if not r.returncode else r.stderr

# check which released definition each workflow is pointing to
result = psql("""
    SELECT w.id, w.name, w.released_definition_id
    FROM workflows w
    WHERE w.id IN (1, 3)
""")
print("Workflows:")
print(result)
