"""Check Dograh container mounts."""
import json, sys, subprocess

result = subprocess.run(
    ['docker', 'inspect', 'aios-dograh-api', '--format', '{{json .Mounts}}'],
    capture_output=True, text=True
)
mounts = json.loads(result.stdout.strip())
for m in mounts:
    print(f"{m['Source']} -> {m['Destination']} [{m['Mode']}]")
