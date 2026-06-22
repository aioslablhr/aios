import subprocess, json

def psql(sql):
    cmd = [
        'docker', 'exec', '-e', 'PGPASSWORD=aios_secret_2026',
        'aios-postgres', 'psql', '-h', 'localhost', '-U', 'aios',
        '-d', 'dograh', '-t', '-A', '-c', sql
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return r.stdout.strip() if not r.returncode else r.stderr

# Check phone number to workflow mapping
result = psql("SELECT id, address, inbound_workflow_id, extra_metadata FROM telephony_phone_numbers")
print("Phone numbers:")
print(result)

# Check latest workflow runs
result = psql("SELECT id, workflow_id, status, created_at FROM workflow_runs ORDER BY id DESC LIMIT 3")
print("\nLatest runs:")
print(result)
