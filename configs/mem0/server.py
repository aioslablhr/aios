import os
import json
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mem0 import Memory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mem0-api")

app = FastAPI(title="AIOS Memory Layer (mem0)", version="1.0.0")

MEM0_CONFIG = json.loads(os.environ.get("MEM0_CONFIG", "{}"))
MEM0_CONFIG.setdefault("vector_store", {
    "provider": "qdrant",
    "config": {
        "host": os.environ.get("QDRANT_HOST", "10.30.0.20"),
        "port": int(os.environ.get("QDRANT_PORT", "6333")),
        "api_key": os.environ.get("QDRANT_API_KEY", ""),
    }
})
MEM0_CONFIG.setdefault("embedder", {
    "provider": "openai",
    "config": {
        "openai_base_url": os.environ.get("EMBEDDING_BASE_URL", "http://10.40.0.10:4000/v1"),
        "model": os.environ.get("EMBEDDING_MODEL", "nomic-embed-text"),
        "api_key": os.environ.get("EMBEDDING_API_KEY", "sk-aios-mem0"),
    }
})
MEM0_CONFIG.setdefault("llm", {
    "provider": "openai",
    "config": {
        "openai_base_url": os.environ.get("LLM_BASE_URL", "http://10.40.0.10:4000/v1"),
        "model": os.environ.get("LLM_MODEL", "gemma-4-31b"),
        "api_key": os.environ.get("LLM_API_KEY", "sk-aios-mem0"),
    }
})

try:
    memory_client = Memory.from_config(MEM0_CONFIG)
    logger.info("mem0 initialized with Qdrant backend")
except Exception as e:
    logger.warning(f"mem0 initialization deferred: {e}")
    memory_client = None


class AddMemoryRequest(BaseModel):
    messages: list[dict] | str
    user_id: str | None = None
    agent_id: str | None = None
    run_id: str | None = None
    metadata: dict | None = None


class SearchMemoryRequest(BaseModel):
    query: str
    user_id: str | None = None
    agent_id: str | None = None
    limit: int = 10


class GetMemoryRequest(BaseModel):
    user_id: str | None = None
    agent_id: str | None = None


@app.post("/v1/memory")
def add_memory(req: AddMemoryRequest):
    if memory_client is None:
        raise HTTPException(status_code=503, detail="mem0 not initialized — embeddings unavailable")
    result = memory_client.add(
        messages=req.messages,
        user_id=req.user_id,
        agent_id=req.agent_id,
        run_id=req.run_id,
        metadata=req.metadata,
    )
    logger.info(f"Memory added: user={req.user_id} agent={req.agent_id} msg_count={len(req.messages) if isinstance(req.messages, list) else 1}")
    return {"status": "ok", "result": result}


@app.post("/v1/search")
def search_memory(req: SearchMemoryRequest):
    if memory_client is None:
        raise HTTPException(status_code=503, detail="mem0 not initialized")
    results = memory_client.search(
        query=req.query,
        user_id=req.user_id,
        agent_id=req.agent_id,
        limit=req.limit,
    )
    return {"status": "ok", "results": results}


@app.get("/v1/memory")
def get_memory(user_id: str | None = None, agent_id: str | None = None):
    if memory_client is None:
        raise HTTPException(status_code=503, detail="mem0 not initialized")
    memories = memory_client.get_all(user_id=user_id, agent_id=agent_id)
    return {"status": "ok", "memories": memories}


@app.delete("/v1/memory/{memory_id}")
def delete_memory(memory_id: str):
    if memory_client is None:
        raise HTTPException(status_code=503, detail="mem0 not initialized")
    memory_client.delete(memory_id=memory_id)
    return {"status": "ok"}


@app.post("/v1/memory/{memory_id}/history")
def get_memory_history(memory_id: str):
    if memory_client is None:
        raise HTTPException(status_code=503, detail="mem0 not initialized")
    history = memory_client.history(memory_id=memory_id)
    return {"status": "ok", "history": history}


@app.get("/health")
def health():
    if memory_client is None:
        return {"status": "deferred", "detail": "Awaiting embedding service (Bifrost/Ollama)"}
    return {"status": "ok", "backend": "qdrant"}


@app.get("/")
def root():
    return {"service": "aios-mem0", "version": "1.0.0", "docs": "/docs"}
