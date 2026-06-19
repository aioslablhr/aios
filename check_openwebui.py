import subprocess, json

result = subprocess.run(
    ["ssh", "ai@10.0.0.100", "docker inspect aios-open-webui"],
    capture_output=True, text=True
)
data = json.loads(result.stdout)
state = data[0]["State"]
print(f"Running: {state.get('Running')}")
print(f"Status: {state.get('Status')}")
print(f"Health: {state.get('Health',{}).get('Status','no check')}")
print(f"Started: {state.get('StartedAt','?')}")
