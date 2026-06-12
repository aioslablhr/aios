import os, json, logging, requests
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm-proxy")
app = FastAPI(title="AIOS LLM Proxy")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://10.40.0.20:11434")

@app.get("/health")
async def health():
    return {"status": "ok", "upstream": OLLAMA_URL}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(path: str, request: Request):
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)
    url = f"{OLLAMA_URL}/{path}"

    if body and "chat/completions" in path:
        try:
            data = json.loads(body)
            had_tools = "tools" in data or "tool_choice" in data
            data.pop("tools", None)
            data.pop("tool_choice", None)
            if had_tools:
                logger.info(f"Stripped tools for Qalb")
            body = json.dumps(data).encode()
        except json.JSONDecodeError:
            pass

    resp = requests.request(
        method=request.method, url=url, data=body,
        headers={k: v for k, v in headers.items() if k.lower() not in ("host", "content-length")},
        stream=True, timeout=300,
    )
    return StreamingResponse(
        content=resp.iter_content(chunk_size=8192),
        status_code=resp.status_code,
        headers={k: v for k, v in resp.headers.items() if k.lower() not in ("transfer-encoding",)},
    )
