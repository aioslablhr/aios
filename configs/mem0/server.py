import os
import json
import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from mem0 import Memory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mem0-api")

app = FastAPI(title="AIOS Memory Layer (mem0)", version="2.0.0")
auth_scheme = HTTPBearer(auto_error=False)

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

memory_client = None
try:
    memory_client = Memory.from_config(MEM0_CONFIG)
    logger.info("mem0 initialized with Qdrant backend")
except Exception as e:
    logger.warning(f"mem0 init deferred: {e}")


def check_auth(creds: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    key = os.environ.get("MEM0_API_KEY", "")
    if key and (not creds or creds.credentials != key):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True


def ensure_client():
    if memory_client is None:
        raise HTTPException(status_code=503, detail="mem0 not initialized")
    return memory_client


# ── Models ──

class AddMemoryRequest(BaseModel):
    messages: list[dict] | str
    user_id: str | None = None
    agent_id: str | None = None
    run_id: str | None = None
    metadata: dict | None = None
    session_id: str | None = None


class SearchMemoryRequest(BaseModel):
    query: str
    user_id: str | None = None
    agent_id: str | None = None
    session_id: str | None = None
    limit: int = 10


class SessionCreateRequest(BaseModel):
    user_id: str
    agent_id: str | None = None
    metadata: dict | None = None


class SessionAppendRequest(BaseModel):
    session_id: str
    role: str = "user"
    content: str
    metadata: dict | None = None


# ── Session Management ──

sessions: dict[str, dict] = {}


@app.post("/v1/sessions")
def create_session(req: SessionCreateRequest):
    mc = ensure_client()
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "id": session_id,
        "user_id": req.user_id,
        "agent_id": req.agent_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "message_count": 0,
        "metadata": req.metadata or {},
    }
    mc.add(
        messages=[{"role": "system", "content": f"Session started for user={req.user_id}"}],
        user_id=req.user_id,
        agent_id=req.agent_id or "default",
        run_id=session_id,
    )
    logger.info(f"Session created: {session_id} for user={req.user_id}")
    return {"session_id": session_id, "status": "ok"}


@app.post("/v1/sessions/{session_id}/append")
def append_to_session(session_id: str, req: SessionAppendRequest):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session = sessions[session_id]
    session["message_count"] += 1
    session["last_active"] = datetime.now(timezone.utc).isoformat()
    mc = ensure_client()
    mc.add(
        messages=[{"role": req.role, "content": req.content}],
        user_id=session["user_id"],
        agent_id=session["agent_id"] or "default",
        run_id=session_id,
        metadata=req.metadata,
    )
    return {"status": "ok", "session_id": session_id, "message_count": session["message_count"]}


@app.get("/v1/sessions/{session_id}")
def get_session(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    mc = ensure_client()
    memories = mc.get_all(user_id=session["user_id"], agent_id=session["agent_id"] or "default")
    return {
        "session": session,
        "memories": memories,
    }


@app.delete("/v1/sessions/{session_id}")
def delete_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    del sessions[session_id]
    return {"status": "ok"}


# ── Memory CRUD ──

@app.post("/v1/memory")
def add_memory(req: AddMemoryRequest, _=Depends(check_auth)):
    mc = ensure_client()
    result = mc.add(
        messages=req.messages,
        user_id=req.user_id,
        agent_id=req.agent_id,
        run_id=req.run_id or req.session_id,
        metadata=req.metadata,
    )
    logger.info(f"Memory added: user={req.user_id} agent={req.agent_id}")
    return {"status": "ok", "result": result}


@app.post("/v1/search")
def search_memory(req: SearchMemoryRequest, _=Depends(check_auth)):
    mc = ensure_client()
    results = mc.search(
        query=req.query,
        user_id=req.user_id,
        agent_id=req.agent_id,
        limit=req.limit,
    )
    return {"status": "ok", "results": results}


@app.get("/v1/memory")
def get_memory(user_id: str | None = None, agent_id: str | None = None, _=Depends(check_auth)):
    mc = ensure_client()
    memories = mc.get_all(user_id=user_id, agent_id=agent_id)
    return {"status": "ok", "memories": memories}


@app.delete("/v1/memory/{memory_id}")
def delete_memory(memory_id: str, _=Depends(check_auth)):
    mc = ensure_client()
    mc.delete(memory_id=memory_id)
    return {"status": "ok"}


@app.post("/v1/memory/{memory_id}/history")
def get_memory_history(memory_id: str, _=Depends(check_auth)):
    mc = ensure_client()
    history = mc.history(memory_id=memory_id)
    return {"status": "ok", "history": history}


@app.post("/v1/batch")
def batch_add(memories: list[AddMemoryRequest], _=Depends(check_auth)):
    mc = ensure_client()
    results = []
    for mem in memories:
        try:
            result = mc.add(messages=mem.messages, user_id=mem.user_id, agent_id=mem.agent_id)
            results.append({"status": "ok", "result": result})
        except Exception as e:
            results.append({"status": "error", "detail": str(e)})
    return {"status": "ok", "results": results}


# ── Health ──

@app.get("/health")
def health():
    if memory_client is None:
        return {"status": "deferred", "detail": "Awaiting embedding service (Bifrost/Ollama)"}
    return {"status": "ok", "backend": "qdrant", "sessions": len(sessions)}


@app.get("/")
def root():
    return {"service": "aios-mem0", "version": "2.0.0", "docs": "/docs"}
