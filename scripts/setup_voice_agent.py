# Run on server to check whisper STT status
import urllib.request, json

# Check Ollama for whisper model
try:
    req = urllib.request.Request("http://10.40.0.20:11434/api/tags")
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    models = [m["name"] for m in data.get("models", [])]
    print(f"Ollama models ({len(models)}):")
    for m in models:
        print(f"  {m}")
    
    has_whisper = any("whisper" in m for m in models)
    if not has_whisper:
        print("\nNo whisper model found. Need to pull one.")
        print("Run: curl http://10.40.0.20:11434/api/pull -d '{\"model\":\"whisper-large-v3-turbo\"}'")
except Exception as e:
    print(f"Ollama check failed: {e}")

# Check n8n health
try:
    req = urllib.request.Request("http://10.20.0.10:5678/healthz")
    resp = urllib.request.urlopen(req, timeout=5)
    print(f"\nn8n health: {resp.status}")
except Exception as e:
    print(f"\nn8n check failed: {e}")

# Check if workflow webhook already exists
try:
    req = urllib.request.Request("http://10.20.0.10:5678/rest/workflows")
    req.add_header("Content-Type", "application/json")
    resp = urllib.request.urlopen(req, timeout=5)
    print(f"\nn8n workflows: {resp.status}")
except Exception as e:
    print(f"\nn8n API check failed: {e}")
