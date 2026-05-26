import json
import os
import httpx
import logging

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aios-mcp")

BIFROST_URL = os.getenv("BIFROST_URL", "http://10.40.0.10:4000")
BIFROST_KEY = os.getenv("BIFROST_ADMIN_KEY", "")
QDRANT_URL = os.getenv("QDRANT_URL", "http://10.30.0.20:6333")
QDRANT_KEY = os.getenv("QDRANT_API_KEY", "")

mcp = FastMCP("aios-mcp", instructions="AIOS MCP Server — exposes Bifrost LLM, Qdrant search, and service registry")

@mcp.tool()
def list_services() -> str:
    """List all AIOS services with their status, IPs, and endpoints"""
    services = {
        "bifrost": {"url": BIFROST_URL, "description": "AI Gateway (LiteLLM)"},
        "qdrant": {"url": QDRANT_URL, "description": "Vector database"},
        "postgres": {"url": "10.30.0.10:5432", "description": "Primary database"},
        "n8n": {"url": "10.20.0.10:5678", "description": "Workflow automation"},
        "ollama": {"url": "10.40.0.20:11434", "description": "Local LLM runner"},
        "langfuse": {"url": "10.60.0.10:3000", "description": "LLM observability"},
        "keycloak": {"url": "10.20.0.40:8080", "description": "SSO / identity"},
        "vault": {"url": "10.0.0.100:8200", "description": "Secrets management"},
        "frigate": {"url": "10.40.0.50:5000", "description": "NVR / object detection"},
        "grafana": {"url": "10.60.0.30:3000", "description": "Dashboards"},
        "prometheus": {"url": "10.60.0.20:9090", "description": "Metrics backend"},
        "clickhouse": {"url": "10.60.0.11:8123", "description": "Analytics database"},
        "dograh": {"url": "10.50.0.30:8080", "description": "Voice agent orchestration"},
        "asterisk": {"url": "10.0.0.100:5060", "description": "SIP PBX"},
        "chatterbox": {"url": "10.40.0.30:4123", "description": "GPU TTS"},
        "mosquitto": {"url": "10.50.0.20:1883", "description": "MQTT event bus"}
    }
    return json.dumps(services, indent=2)

@mcp.tool()
async def llm_chat(model: str, messages: list) -> str:
    """Send a chat request through Bifrost AI Gateway. Returns the model response."""
    headers = {"Content-Type": "application/json"}
    if BIFROST_KEY:
        headers["Authorization"] = f"Bearer {BIFROST_KEY}"
    payload = {"model": model, "messages": messages}
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(f"{BIFROST_URL}/v1/chat/completions", json=payload, headers=headers)
        resp.raise_for_status()
        return json.dumps(resp.json(), indent=2)

@mcp.tool()
async def qdrant_search(collection: str, vector: list, limit: int = 5) -> str:
    """Search a Qdrant collection by vector. Returns top-k matches."""
    headers = {"Content-Type": "application/json"}
    if QDRANT_KEY:
        headers["api-key"] = QDRANT_KEY
    payload = {"vector": vector, "limit": limit, "with_payload": True}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{QDRANT_URL}/collections/{collection}/points/search", json=payload, headers=headers)
        resp.raise_for_status()
        return json.dumps(resp.json(), indent=2)

@mcp.tool()
async def list_collections() -> str:
    """List all collections in Qdrant vector database."""
    headers = {}
    if QDRANT_KEY:
        headers["api-key"] = QDRANT_KEY
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{QDRANT_URL}/collections", headers=headers)
        resp.raise_for_status()
        return json.dumps(resp.json(), indent=2)

if __name__ == "__main__":
    mcp.run(transport="sse")
